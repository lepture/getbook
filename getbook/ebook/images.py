import logging
import mimetypes
import hashlib
import os
from urllib.parse import urlparse

import requests
from PIL import Image

log = logging.getLogger(__name__)

THUMBNAIL_WIDTH = 625
THUMBNAIL_HEIGHT = 1000

IMAGE_EXTENSIONS = ['jpeg', 'png', 'gif', 'svg']
LIMIT_EXTENSIONS = ['.jpeg', '.png', '.jpg']


def fetch_thumbnail(src, image_dir, referrer=None):
    name = hashlib.sha1(src.encode('utf-8')).hexdigest()
    dest = _find_in_cache(name, None, image_dir)
    if dest:
        return dest

    filepath = get_or_download_image(src, image_dir, referrer)
    if not filepath:
        return None

    ext = os.path.splitext(filepath)[-1]
    if ext not in LIMIT_EXTENSIONS:
        return filepath

    dest = os.path.join(image_dir, '{}.jpg'.format(name))
    folder = os.path.dirname(dest)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    try:
        img = Image.open(filepath, 'r')
        img.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
        img.save(dest, optimize=True, quality=75)
    except OSError:
        return None
    return dest


def get_or_download_image(src, image_dir, referrer=None):
    name = hashlib.sha1(src.encode('utf-8')).hexdigest()
    d = urlparse(src)
    ct = mimetypes.guess_type(d.path)[0]
    ext = _get_extname(ct)
    dest = _find_in_cache(name, ext, image_dir)
    if dest:
        return dest

    try:
        if referrer:
            headers = {'Referer': referrer}
        else:
            headers = None
        req = requests.get(src, timeout=15, stream=True, headers=headers)
    except Exception as e:
        log.exception(e)
        return None

    if req.status_code != 200:
        return None

    if not ext:
        ext = _get_extname(req.headers.get('Content-Type'))

    if not ext:
        return None

    dest = os.path.join(image_dir, '{}.{}'.format(name, ext))
    folder = os.path.dirname(dest)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    with open(dest, 'wb') as f:
        for chunk in req:
            f.write(chunk)
    return dest


def _find_in_cache(name, ext, image_dir):
    if ext:
        ext_names = [ext]
    else:
        ext_names = IMAGE_EXTENSIONS

    for suffix in ext_names:
        dest = os.path.join(image_dir, '{}.{}'.format(name, suffix))
        if os.path.isfile(dest):
            return dest


def _get_extname(content_type):
    if content_type and content_type.startswith('image/'):
        name = content_type.replace('image/', '').split(';')[0]
        return name.split('+')[0]
