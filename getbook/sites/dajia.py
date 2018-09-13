import requests
import time
from ..core import Parser, Book
from ..core.utils import to_datetime

REFERRER = 'http://dajia.qq.com/author_personal.htm'
WZ_URL = 'http://i.match.qq.com/ninjayc/dajiawenzhanglist'
CHANNEL_URL = 'http://i.match.qq.com/ninjayc/dajialanmu'
USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36'
)

AUTHOR_PATTERN = 'http://dajia.qq.com/author_personal.htm#!/'
CHANNEL_PATTERN = 'http://dajia.qq.com/tanzi_diceng.htm#!/'


class DajiaParser(Parser):
    NAME = 'qq-dajia'
    SOUP_FEATURES = 'html.parser'
    ALLOWED_DOMAINS = ['dajia.qq.com']

    @classmethod
    def check_url(cls, url):
        return True

    @classmethod
    def normalize_url(cls, url):
        return url

    def parse(self):
        if self.url.startswith(AUTHOR_PATTERN):
            author_id = self.url.replace(AUTHOR_PATTERN, '')
            return parse_dajia_author(author_id.strip())

        if self.url.startswith(CHANNEL_PATTERN):
            channel_id = self.url.replace(CHANNEL_PATTERN, '')
            return parse_dajia_channel(channel_id.strip())

        return super(DajiaParser, self).parse()

    def parse_lang(self):
        return 'zh'

    def parse_publisher(self):
        return u'大家'

    def parse_summary(self):
        el = self.dom.find('div', class_='dao_content')
        if el:
            return el.get_text()

    def parse_pubdate(self):
        el = self.dom.find('span', class_='publishtime')
        if el:
            return to_datetime(el.get_text().strip())

    def parse_author(self):
        els = self.dom.select('img[alt="authorImg"] + a')
        if els:
            return els[0].get_text()

    def parse_title(self):
        el = self.dom.find('title')
        if el:
            title = el.get_text()
            return title.strip()

    def parse_content(self):
        return self.dom.find('div', id='articleContent')


def parse_dajia_author(author_id):
    headers = {'User-Agent': USER_AGENT, 'Referer': REFERRER}
    t = int(time.time())

    params = {'action': 'wz', 'authorid': author_id, '_': t}
    resp = requests.get(WZ_URL, headers=headers, params=params)
    if resp.status_code != 200:
        return None

    data = resp.json()
    entries = data.get('data')
    if not entries:
        return None

    latest = entries[0]
    author = latest.get('name')

    uid = 'dajia-a-{}'.format(author_id)
    book = Book(uid=uid, title=author, lang='zh', author=author)
    book.chapters = [format_item(item) for item in entries]
    return book


def parse_dajia_channel(channel_id):
    headers = {'User-Agent': USER_AGENT, 'Referer': REFERRER}
    t = int(time.time())

    params = {'action': 'wz', 'channelid': channel_id, '_': t}
    resp = requests.get(WZ_URL, headers=headers, params=params)
    if resp.status_code != 200:
        return None

    data = resp.json()
    entries = data.get('data')
    if not entries:
        return None

    params = {'action': 'lanmu', 'channelid': channel_id, '_': t}
    resp = requests.get(CHANNEL_URL, headers=headers, params=params)
    data = resp.json()
    title = data['data']['channel']['n_cname']

    uid = 'dajia-c-{}'.format(channel_id)
    book = Book(uid=uid, title=title, lang='zh')
    book.chapters = [format_item(item) for item in entries]
    return book


def format_item(item):
    published = item['n_publishtime']
    published = published.replace(' ', 'T') + '+08:00'
    return {
        'title': item['n_title'],
        'url': item['n_url'],
        'pubdate': published,
    }
