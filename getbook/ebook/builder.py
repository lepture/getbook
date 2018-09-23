import os
import re
import shutil
import zipfile
import logging
import requests

from collections import Counter
from subprocess import Popen, PIPE
from .processor import replace_content_images, create_book_cover
from ._jinja import create_jinja
from .. import __homepage__ as homepage

log = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
with open(os.path.join(STATIC_DIR, 'container.xml'), 'rb') as f:
    EPUB_CONTAINER = f.read()
EPUB_MIME_TYPE = b'application/epub+zip'
STYLE_WHITE_SPACE = re.compile(r'\n+\s*')


class BookBuilder(object):
    _jinja = create_jinja()

    def __init__(self, book, cache_dir, config, kindlegen=None):
        config.setdefault('GENERATOR_NAME', 'getbook')
        config.setdefault('GENERATOR_URL', homepage)

        self.book = book
        self.config = config
        self.kindlegen = kindlegen
        self.cache_dir = cache_dir
        self.book_dir = os.path.join(cache_dir, 'book', book.uid)

        self._lang_counter = Counter()
        self._cover = None

        if not os.path.isdir(self.book_dir):
            os.makedirs(self.book_dir)

    def write_template(self, template, params, dest):
        tpl = self._jinja.get_template(template)
        content = tpl.render(params)
        self._write(content, dest)

    def write_chapter(self, chapter):
        image_dir = os.path.join(self.cache_dir, 'img')
        for img in replace_content_images(chapter, image_dir):
            self.book.images.add(img)
            dest = os.path.join(self.book_dir, img.href)
            shutil.copy(img.filepath, dest)

        self.write_template(
            'chapter.html',
            {'chapter': chapter},
            '{}.xhtml'.format(chapter['uid'])
        )
        self._process_chapter(chapter)

    def write_section(self, section):
        self.write_template(
            'section.html',
            {'section': section},
            '{}.xhtml'.format(section.uid)
        )

    def write_toc(self, book):
        self.write_template('toc.html', {'book': book}, 'toc.xhtml')

    def write_meta(self, book):
        self.write_template('cover.html', {'book': book}, 'cover.xhtml')
        if book.lang == 'zh':
            tpl = 'book.preface.zh.html'
        else:
            tpl = 'book.preface.en.html'
        self.write_template(
            tpl,
            {'book': book, 'config': self.config},
            'preface.xhtml'
        )

    def write_stylesheet(self, *names):
        style = ''.join([read_static_file(n) for n in names])
        style = STYLE_WHITE_SPACE.sub('', style)
        self._write(style, 'stylesheet.css')

    def write_cover(self, book):
        if not self.config:
            book.cover = None
            return False

        image_dir = os.path.join(self.cache_dir, 'img')

        def _create_cover(src):
            cover = create_book_cover(self.config, book, src, image_dir)
            if cover:
                cover.save(os.path.join(self.book_dir, 'cover.jpg'))
                book.cover = src
                return True
            return False

        if book.cover and _create_cover(book.cover):
            return True

        if self._cover and _create_cover(self._cover['src']):
            return True

        return _create_cover(self._get_unsplash_cover())

    def write_opf(self, book):
        self.write_template(
            'book.opf.xml',
            {'book': book, 'config': self.config},
            'package.opf'
        )

    def create_mobi(self, output):
        opf_file = os.path.join(self.book_dir, 'package.opf')
        cmd = [self.kindlegen, '-dont_append_source', opf_file]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        if b'Error' in stdout:
            raise RuntimeError(stdout)

        mobi_file = os.path.join(self.book_dir, 'package.mobi')
        shutil.move(mobi_file, output)

    def create_epub(self, output):
        with zipfile.ZipFile(output, 'w') as z:
            z.writestr('META-INF/container.xml', EPUB_CONTAINER)
            z.writestr('mimetype', EPUB_MIME_TYPE)

            for name in os.listdir(self.book_dir):
                if name.endswith('.mobi'):
                    continue
                filepath = os.path.join(self.book_dir, name)
                with open(filepath, 'rb') as f:
                    content = f.read()
                    z.writestr('OEBPS/' + name, content)

    def build(self, output, epub=True, mobi=True):
        book = self._prepare_book()
        self.write_cover(book)

        for sec in book.sections:
            self.write_section(sec)

        self.write_toc(book)
        self.write_meta(book)
        self.write_opf(book)

        if not os.path.isdir(output):
            os.makedirs(output)

        if epub:
            dest = os.path.join(output, book.uid + '.epub')
            self.write_stylesheet('reset', 'layout', 'highlight', 'epub')
            log.info('EPUB: {}'.format(dest))
            self.create_epub(dest)

        if mobi and self.kindlegen:
            dest = os.path.join(output, book.uid + '.mobi')
            self.write_stylesheet('reset', 'layout', 'mobi')
            log.info('MOBI: {}'.format(dest))
            self.create_mobi(dest)
        # self.cleanup()

    def _prepare_book(self):
        if not self._lang_counter:
            lang = 'en'
        else:
            lang = self._lang_counter.most_common(1)[0][0]

        book = self.book
        book.lang = lang
        return book

    def _process_chapter(self, chapter):
        lang = chapter.get('lang')
        if lang != 'en':
            self._lang_counter[lang] += 1

        if self._cover:
            w = self._cover['width']
            h = self._cover['height']
            if w >= 1000 and h >= 800:
                return

        image = chapter.get('image')
        if image:
            self._cover = image

    def _get_unsplash_cover(self):
        client_id = self.config.get('UNSPLASH_CLIENT_ID')
        if not client_id:
            return None
        url = 'https://api.unsplash.com/photos/random'
        resp = requests.get(url, params={'client_id': client_id})
        data = resp.json()
        return data['urls']['full']

    def _write(self, content, dest):
        if not isinstance(content, bytes):
            content = content.encode('utf-8')

        dest = os.path.join(self.book_dir, dest)
        with open(dest, 'wb') as f:
            f.write(content)


def read_static_file(name):
    filepath = os.path.join(STATIC_DIR, name) + '.css'
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
