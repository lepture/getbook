import re
from ..core import Parser, Book

BOOK_PATTERN = re.compile(r'/html/(\d+)/(\d+)/$')
PAGE_PATTERN = re.compile(r'/html/\d+/\d+/\d+\.html$')


class PiaotianParser(Parser):
    NAME = 'piaotian'
    ALLOWED_DOMAINS = ['www.piaotian.com']
    SOUP_FEATURES = 'html5lib'

    @classmethod
    def check_url(cls, url):
        return True

    def parse(self):
        m = BOOK_PATTERN.findall(self.url)
        if m:
            book_id = '{}-{}'.format(*m[0])
            return self.parse_book(book_id)
        return super(PiaotianParser, self).parse()

    def parse_book(self, book_id):
        self.fetch()
        uid = '{}-{}'.format(self.NAME, book_id)
        el = self.dom.find('h1')
        title = el.get_text()
        title = title.replace(u'最新章节', '')
        book = Book(uid, title, lang='zh')

        el = self.dom.find('meta', attrs={'name': 'author'})
        author = el.get('content')
        book.author = author
        book.chapters = list(self._parse_book_chapters())
        return book

    def parse_lang(self):
        return 'zh'

    def parse_publisher(self):
        return u'飘天文学'

    def parse_title(self):
        el = self.dom.find('h1')
        link = el.find('a')
        link.extract()
        title = el.get_text()
        title = title.replace(u'正文', '')
        el.extract()
        return title.strip()

    def parse_content(self):
        rules = [
            'body > div',
            'body > table',
            'body > center',
            'body > a',
        ]
        for el in self.select_by_rules(rules):
            el.extract()

        node = self.dom.find('body')
        node.name = 'div'
        return node

    def _parse_book_chapters(self):
        els = self.dom.select('li > a')
        for el in els:
            href = el.get('href')
            href = self.urljoin(href)
            title = el.get_text()
            yield {'title': title, 'url': href}
