import re
from bs4 import BeautifulSoup
from ..core import Parser, Book, Section

PAGE_PATTERN_1 = re.compile(r'/book\d*/(\d+)/(\d+).html')
PAGE_PATTERN_2 = re.compile(
    r'(?:files\/\w+|wuxia|tuili)'
    r'/\d{4}(?:\d\d)?/(\d+)/(\d+).html'
)
BOOK_PATTERN_1 = re.compile(r'/book\d*/(\d+)/(?:index.html)?$')
BOOK_PATTERN_2 = re.compile(
    r'(?:files\/\w+|wuxia|tuili)'
    r'/\d{4}(?:\d\d)?/(\d+).html$'
)
META_PATTERN = re.compile(u'作者：(.*)发布时间：(.*)')


class KanunuParser(Parser):
    NAME = 'kanunu'
    ALLOWED_DOMAINS = ['www.kanunu8.com']

    @classmethod
    def check_url(cls, url):
        return True

    def parse(self):
        m = BOOK_PATTERN_1.findall(self.url)
        if m:
            return self.parse_book(m[0])
        m = BOOK_PATTERN_2.findall(self.url)
        if m:
            return self.parse_book(m[0])
        return super(KanunuParser, self).parse()

    def parse_book(self, book_id):
        self.fetch()
        uid = '{}-{}'.format(self.NAME, book_id)
        els = self.dom.select('h1 > strong')
        if not els:
            els = self.dom.select('h2 > b')
        if els:
            title = els[0].get_text()
        else:
            title = 'Unknown'

        book = Book(uid, title, lang='zh')
        for el in self.dom.select('td'):
            text = el.get_text()
            m = META_PATTERN.findall(text)
            if m:
                group = m[0]
                book.author = group[0].strip()
                book.pubdate = group[1].strip()

        for item in self._parse_book_chapters():
            if isinstance(item, Section):
                book.add_section(item)
            else:
                book.chapters.append(item)
        return book

    def parse_lang(self):
        return 'zh'

    def parse_publisher(self):
        return 'Kanunu'

    def parse_title(self):
        el = self.dom.find('font')
        if el:
            title = el.get_text()
            title = title.replace(u'正文', '')
            return title.strip()

    def parse_content(self):
        els = self.dom.select('td > p')
        if len(els) == 1:
            return els[0]
        html = '\n'.join([el.decode_contents() for el in els])
        return BeautifulSoup(html, self.SOUP_FEATURES)

    def _parse_book_chapters(self):
        section_elements = self.dom.find_all(
            'tr',
            attrs={'align': 'center', 'bgcolor': '#ffffcc'}
        )
        has_section = len(section_elements) > 1

        section = None

        rule = 'table[bgcolor="#d4d0c8"] tr'
        for el in self.dom.select(rule):
            bgcolor = el.get('bgcolor')
            if bgcolor and bgcolor == '#ffffcc' and has_section:
                title = el.get_text()
                section = Section(title=title)
                yield section
                continue

            for link in el.select('td > a'):
                href = link.get('href')
                title = link.get_text()
                href = self.urljoin(href)
                chapter = {'title': title, 'url': href}
                if section:
                    section.chapters.append(chapter)
                else:
                    yield chapter
