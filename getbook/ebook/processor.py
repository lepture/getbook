import os
import json
import logging
import mimetypes
from PIL import Image
from bs4 import BeautifulSoup
from .cover import Cover
from .images import fetch_thumbnail, get_or_download_image
from ..core import LXML_SPACE
from ..core import Image as ImageModel
from ..core.utils import format_date

log = logging.getLogger(__name__)


def replace_content_images(data, image_dir):
    referrer = data['url']
    content = '<div>{}</div>'.format(data['content'])
    dom = BeautifulSoup(content, LXML_SPACE)

    for tag in dom.select('.tag-img'):
        attrs = json.loads(tag.get('data-attrs'))
        src = attrs.get('src')
        if not src:
            del tag.attrs['data-attrs']
            continue

        image = generate_thumbnail_image(src, image_dir, referrer)
        if not image:
            del tag.attrs['data-attrs']
            continue
        yield image

        img = dom.new_tag('img')
        img['src'] = image.href
        tag.replace_with(img)

    body = dom.find('div')
    content = ''.join([str(el) for el in body.contents])
    data['content'] = content


def generate_thumbnail_image(src, image_dir, referrer):
    log.debug('Fetching: {}'.format(src))
    filepath = fetch_thumbnail(src.strip(), image_dir, referrer)
    if not filepath:
        return
    href = os.path.basename(filepath)
    uid = href.split('.')[0]
    ct = mimetypes.guess_type(filepath)[0]
    return ImageModel(uid=uid, filepath=filepath, href=href, mimetype=ct)


def update_chapter_image(data, image_dir):
    image = data.get('image')
    attachments = data.get('attachments')
    if attachments:
        images = attachments.get('img')
    else:
        images = None

    if not image and not images:
        return data

    best_cover = None
    if image and 'src' in image:
        size = _get_image_size(image['src'], image_dir)
        if size:
            image['width'], image['height'] = size
            best_cover = image

    if images:
        _calc_chapter_image(data, images, best_cover, image_dir)
    return data


def _calc_chapter_image(data, images, best_cover, image_dir):
    alt_src = None
    alt_size = (0, 0)
    for img in images:
        src = img.get('src')
        if not src:
            continue

        size = _get_image_size(src, image_dir)
        if not size:
            continue

        w, h = size
        img['width'], img['height'] = w, h

        if best_cover:
            continue

        if w > 600 and h > 858:
            best_cover = {'src': src, 'width': w, 'height': h}
        elif w > alt_size[0] and h > 480:
            alt_src = src
            alt_size = (w, h)

    if best_cover:
        data['image'] = best_cover
    elif alt_src:
        data['image'] = {
            'src': alt_src,
            'width': alt_size[0],
            'height': alt_size[1]
        }
    return data


def _get_image_size(src, image_dir):
    filepath = get_or_download_image(src.strip(), image_dir)
    if filepath and _is_valid_image(filepath):
        img = Image.open(filepath)
        return img.size


def _is_valid_image(filepath):
    suffix = ['.jpeg', '.jpg', '.png']
    for k in suffix:
        if filepath.endswith(k):
            return True
    return False


def create_book_cover(config, book, src, image_dir):
    if not src:
        return None

    cover_file = get_or_download_image(src, image_dir)
    ext = cover_file.split('.')[-1]
    if ext not in ['jpg', 'jpeg', 'png']:
        return None

    cover = Cover(config)
    cover.draw_background(cover_file)

    pubdate = format_date(book.pubdate, '%Y.%m.%d')
    cover.draw_top_text(pubdate)
    cover.draw_title_text(book.title)
    cover.draw_bottom_text(book.author.upper())
    return cover
