import re
from ..core import Parser, Book, Section

BOOK_PATTERN = re.compile(r'/xiaoshuo/(\d+)/(\d+)/$')
PAGE_PATTERN = re.compile(r'/xiaoshuo/\d+/\d+/\d+\.html$')


class Qbxs5Parser(Parser):
    NAME = 'qbxs5'
    ALLOWED_DOMAINS = ['www.qbxs5.com']
    SOUP_FEATURES = 'html5lib'

    @classmethod
    def check_url(cls, url):
        return True

    def parse(self):
        m = BOOK_PATTERN.findall(self.url)
        if m:
            book_id = '{}-{}'.format(*m[0])
            return self.parse_book(book_id)
        return super(Qbxs5Parser, self).parse()

    def parse_book(self, book_id):
        self.fetch()
        uid = '{}-{}'.format(self.NAME, book_id)
        el = self.dom.find('h1')
        title = el.get_text()
        book = Book(uid, title, lang='zh')

        els = self.dom.select('div#smallcons a')
        if els:
            el = els[0]
            author = el.get_text()
            book.author = author

        for item in self._parse_book_chapters():
            if isinstance(item, Section):
                book.add_section(item)
            else:
                book.chapters.append(item)
        return book

    def parse_lang(self):
        return 'zh'

    def parse_publisher(self):
        return u'全本小说屋'

    def parse_title(self):
        el = self.dom.find('h1')
        title = el.get_text()
        return title.strip()

    def parse_content(self):
        return self.dom.find('div', id='content')

    def _parse_book_chapters(self):
        els = self.dom.select('div#readerlist li')
        section = None
        for el in els:
            node = el.find('h3')
            if node:
                title = node.get_text()
                section = Section(title=title)
                yield section
                continue

            node = el.find('a')
            href = node.get('href')
            href = self.urljoin(href)
            title = node.get_text()
            chapter = {'title': title, 'url': href}
            section.chapters.append(chapter)
