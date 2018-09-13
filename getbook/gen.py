import os
import json
import logging
import datetime
from .core import Book
from .core.utils import sha1name, to_datetime
from .parser import Readable
from .ebook import BookBuilder
from .ebook.processor import update_chapter_image

log = logging.getLogger(__name__)


class BookGen(object):
    def __init__(self, config, kindlegen=None, cache_dir=None):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser('~'), '.getbook/1')
        self.config = config
        self.kindlegen = kindlegen
        self.cache_dir = cache_dir
        self._ensure_folders(['data', 'book', 'img'])

    def _ensure_folders(self, names):
        for k in names:
            folder = os.path.join(self.cache_dir, k)
            if not os.path.isdir(folder):
                os.makedirs(folder)

    def gen_cache_file(self, url):
        name = sha1name(url)
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

        builder = BookBuilder(
            book, self.cache_dir,
            config=self.config,
            kindlegen=self.kindlegen,
        )
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
        except Exception as e:
            log.warn('Error: {!r}'.format(e))
            return None

        data = chapter.to_dict()
        log.info('From network: {}'.format(data['title']))

        update_chapter_image(data, os.path.join(self.cache_dir, 'img'))
        with open(filepath, 'w') as f:
            json.dump(data, f, cls=JSONEncoder)
        return data

    def _write_chapter(self, book, force=False, builder=None):
        chapter_index = 0

        def _parse_chapter(chapter, index):
            data = self.parse(c['url'], force)
            index += 1
            if data:
                uid = 'c-{}'.format(index)
                c['uid'] = uid
                c['status'] = 'success'
                if 'title' not in c:
                    c['title'] = data['title']

                data['uid'] = uid
                if builder:
                    builder.write_chapter(data)
            else:
                c['status'] = 'error'
            return index

        for c in book.chapters:
            chapter_index = _parse_chapter(c, chapter_index)

        for s in book.sections:
            for c in s.chapters:
                chapter_index = _parse_chapter(c, chapter_index)

        return book


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def filter_book_chapters(book, start=None, end=None):

    def _filter_chapter(chapter):
        pubdate = chapter.get('pubdate')
        if not pubdate:
            return True

        pubdate = to_datetime(pubdate)
        if start and pubdate <= start:
            return False
        if end and pubdate > end:
            return False
        return True

    book.chapters = [c for c in book.chapters if _filter_chapter(c)]
    for s in book.sections:
        s.chapters = [c for c in s.chapters if _filter_chapter(c)]
    return book
