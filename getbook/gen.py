import os
import json
import hashlib
import logging
import datetime
from .core import Book
from .parser import Readable
from .ebook import BookBuilder

log = logging.getLogger(__name__)


class BookGen(object):
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser('~'), '.getbook')
        self.cache_dir = cache_dir
        self._ensure_folders(['data', 'book'])

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

    def parse(self, url, force=False):
        log.debug('Fetching: {}'.format(url))

        filepath = self.gen_cache_file(url)
        if os.path.isfile(filepath) and not force:
            return self._parse_from_cache(url, filepath)
        return self._parse_from_network(url, filepath)

    def build(self, book, output=None, force=False):
        if output is None:
            output = os.getcwd()

        builder = BookBuilder(book, self.cache_dir)
        self._write_chapter(book, force=force, builder=builder)
        builder.build(output)

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
            if isinstance(chapter, Book):
                return chapter
        except:
            log.warn('Error: {}'.format(url))
            return None

        data = chapter.to_dict()
        log.info('From network: {}'.format(data['title']))

        with open(filepath, 'w') as f:
            json.dump(data, f, cls=JSONEncoder)
        return data

    def _write_chapter(self, book, force=False, builder=None):
        chapter_index = 0
        
        def _parse_chapter(chapter):
            data = self.parse(c['url'], force)
            chapter_index += 1
            if data:
                chapter_id = 'c-{}'.format(chapter_index)
                c['id'] = chapter_id
                c['status'] = 'success'
                if 'title' not in c:
                    c['title'] = data['title']

                data['id'] = chapter_id
                if builder:
                    builder.write_chapter(data)
            else:
                c['status'] = 'error'

        for c in book.chapters:
            _parse_chapter(c)

        for s in book.sections:
            for c in s.chapters:
                _parse_chapter(c)

        return book


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        print(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
