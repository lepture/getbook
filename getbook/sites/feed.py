from ..core import Parser, Book
from ..core.utils import sha1name


class FeedParser(Parser):
    NAME = 'feed'
    SOUP_FEATURES = 'xml'

    @classmethod
    def check_html(cls, html):
        text = html[-40:]
        if '</rss>' in text and '</channel>' in text:
            return True
        if '</entry>' in text and '</feed>' in text:
            return True

    def parse(self):
        el = self.dom.find('title')
        if el:
            title = el.get_text()
        else:
            title = None
        items = self.dom.find_all('item')
        if not items:
            items = self.dom.find_all('entry')

        if not items:
            raise ValueError('Not valid feed')

        uid = 'feed-{}'.format(sha1name(self.url)[:6])

        el = self.dom.get('language')
        if el:
            lang = el.get_text().strip()
        else:
            lang = None

        book = Book(uid=uid, title=title, lang=lang)
        book.chapters = [_parse_item(item) for item in items]
        return book


def _parse_item(item):
    el = item.find('title')
    title = el.get_text()
    if title:
        title = title.strip()

    el = item.find('link')
    href = el.get('href')
    if href:
        href = href.strip()
    if not href:
        href = el.get_text()
    if href:
        href = href.strip()

    data = dict(
        title=title,
        url=href,
    )
    el = item.find('pubdate')
    if not el:
        el = item.find('updated')
    if not el:
        el = item.find('published')

    if el:
        pubdate = el.get_text()
        if pubdate:
            data['pubdate'] = pubdate
    return data
