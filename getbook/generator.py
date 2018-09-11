import os
import json
import hashlib
import logging
import datetime
from .parser import Readable

log = logging.getLogger(__name__)


class Generator(object):
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser('~'), '.getbook')
        self.cache_dir = cache_dir
        self._ensure_folders(['data'])

    def _ensure_folders(self, names):
        for k in names:
            folder = os.path.join(self.cache_dir, k)
            if not os.path.isdir(folder):
                os.makedirs(folder)

    def gen_cache_file(self, url):
        # TODO: image
        if not isinstance(url, bytes):
            url = url.encode('utf-8')
        name = hashlib.sha1(url).hexdigest()
        return os.path.join(self.cache_dir, 'data', name + '.json')

    def parse(self, url):
        log.debug('Fetching: {}'.format(url))

        filepath = self.gen_cache_file(url)
        if os.path.isfile(filepath):
            return self._parse_from_cache(url, filepath)
        return self._parse_from_network(url, filepath)

    def _parse_from_cache(self, url, filepath):
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
                log.info('From cache: {}'.format(data['title']))
            except Exception:
                data = self._parse_from_network(url, filepath)
        return data

    def _parse_from_network(self, url, filepath):
        parser = Readable(url)
        try:
            chapter = parser.parse(True)
        except:
            log.warn('Error: {}'.format(url))
            return None

        data = chapter.to_dict()
        log.info('From network: {}'.format(data['title']))

        with open(filepath, 'w') as f:
            json.dump(data, f, cls=JSONEncoder)
        return data


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        print(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
