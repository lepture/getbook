# coding: utf-8

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from bs4.builder import builder_registry
from bs4.builder._lxml import LXMLTreeBuilder

from .post_clean import parse_content_and_attachments
from .parse_lang import parse_lang_by_text
from .utils import normalize_url, get_canonical_link
from .models import Chapter

KILL_TAGS = [
    'button', 'input', 'select', 'textarea',
    'label', 'optgroup', 'command', 'datalist',
    'script', 'noscript', 'style',
    'frame', 'frameset', 'noframes',
    'canvas', 'applet', 'map', 'nav',
    'blink', 'marquee', 'area', 'base', 'svg',
]

DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12'
    ' (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12'
    ' facebookexternalhit/1.1 Facebot Twitterbot/1.0'
)
CHARSET_PATTERN = re.compile(r'<meta.*(charset="?\w+"?).*?>', re.I)
LXML_SPACE = 'lxml-space'


class TreeBuilder(LXMLTreeBuilder):
    NAME = LXML_SPACE
    features = [NAME]
    preserve_whitespace_tags = {'td', 'pre'}


builder_registry.register(TreeBuilder)


class Parser(object):
    NAME = None
    ENCODING = None
    USER_AGENT = DEFAULT_USER_AGENT
    SOUP_FEATURES = LXML_SPACE

    @classmethod
    def normalize_url(cls, url):
        return normalize_url(url)

    def __init__(self, url, content=None):
        self.url = url
        self.content = content

    def _request(self, url):
        user_agent = self.get_user_agent(url)
        headers = {'User-Agent': user_agent}
        req = requests.get(url, timeout=5, headers=headers)

        if req.status_code != 200:
            raise RuntimeError("Not available %s" % req.status_code)

        if not req.content:
            raise RuntimeError("No content")

        return req

    def get_user_agent(self, url):
        return self.USER_AGENT

    def parse_lang(self):
        raise NotImplementedError()

    def parse_publisher(self):
        raise NotImplementedError()

    def parse_title(self):
        raise NotImplementedError()

    def parse_content(self):
        raise NotImplementedError()

    def parse_summary(self):
        return None

    def parse_author(self):
        return None

    def parse_pubdate(self):
        return None

    def parse_image(self):
        return None

    def fetch(self):
        req = self._request(self.url)

        if not self.ENCODING:
            if 'charset' in req.headers.get('content-type', '').lower():
                charset = req.encoding.lower()
            else:
                charset = get_html_charset(req.text)

            if charset:
                if charset == 'gb2312':
                    charset = 'gbk'
                elif charset == 'iso-8859-1':
                    charset = 'utf-8'
                req.encoding = charset

        self.content = re.sub(r'\r\n|\r', '\n', req.text)

        # parse canonical link
        link = get_canonical_link(self.dom)
        if link:
            self.url = link
        else:
            self.url = req.url

    def before_parse(self):
        if self.content is None:
            self.fetch()

    def parse(self):
        self.before_parse()

        # clean useless tags
        clean_soup(self.dom)

        # parsing article content
        content_node = self.parse_content()
        if not content_node:
            raise RuntimeError('No content')

        # parsing article info
        author = safe_strip(self.parse_author())
        summary = safe_strip(self.parse_summary())
        pubdate = self.parse_pubdate()
        image = self.parse_image()
        title = safe_strip(self.parse_title())

        # parsing site info
        lang = self.parse_lang()
        if not lang and title:
            lang = parse_lang_by_text(title) or 'en'

        publisher = safe_strip(self.parse_publisher())

        self.make_absolute_links(content_node)
        content, attachments = parse_content_and_attachments(
            content_node, self.dom
        )

        if not summary and content_node:
            summary = content_node.get_text()

        if summary:
            summary = safe_strip(summary)[:120]

        return Chapter(
            self.url, lang, image, publisher,
            author, title, summary,
            content, pubdate, attachments,
        )

    @property
    def dom(self):
        dom = getattr(self, '_dom', None)
        if dom is not None:
            return dom
        dom = BeautifulSoup(self.content, self.SOUP_FEATURES)
        self._dom = dom
        return self._dom

    def create_attachment_tag(self, name, src, **kwargs):
        node = self.dom.new_tag('span')
        node['class'] = 'tag tag-{}'.format(name)
        node['data-attachment'] = name
        node['data-src'] = src
        for key in kwargs:
            node[key] = kwargs[key]
        node.string = name
        return node

    def select_by_rules(self, rules):
        for rule in rules:
            for el in self.dom.select(rule):
                yield el

    def urljoin(self, src):
        return urljoin(self.url, src)

    def make_absolute_links(self, node):
        valid_sources = ['http', '//', '#']

        def _is_valid(s):
            for p in valid_sources:
                if s.startswith(p):
                    return True
            return False

        for el in node.find_all('a'):
            href = el.get('href')
            if href and not _is_valid(href):
                el['href'] = self.urljoin(href)

        for el in node.select('[src]'):
            src = el.get('src')
            if src:
                el['src'] = self.urljoin(src)


def clean_soup(dom):
    # clean comments
    for el in dom.find_all(text=lambda text: isinstance(text, Comment)):
        el.extract()

    for el in dom.find_all(KILL_TAGS):
        el.extract()


def get_html_charset(html):
    m = CHARSET_PATTERN.findall(html)
    if m:
        charset = m[0].lower()
        charset = charset.replace('charset=', '')
        return charset.strip('"')


def safe_strip(text):
    if text:
        return text.strip()
    return text
