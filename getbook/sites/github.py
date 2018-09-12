# coding: utf-8

import re

from bs4 import BeautifulSoup

from ..core import Parser
from ..core.utils import to_datetime, get_first_child

LXML_GIST = 'lxml-gist'
GIST_TAG = re.compile(
    r'''<div[^>]*data-attachment=(?:'|")gist(?:'|")[^>]*>gist</div>'''
)
GIST_URL = re.compile(
    r'''data-src=(?:'|")'''
    r'(https://gist\.github\.com/(?:\d+|(?:[^/]+/[a-z0-9]+)))'
    r'''(?:'|")'''
)


class GithubIssueParser(Parser):
    NAME = 'github-issue'
    ALLOWED_DOMAINS = ['github.com']
    URL_PATTERN = re.compile(r'https://github\.com/.*?/(?:issues|pull)/\d+')

    @classmethod
    def check_url(cls, url):
        return cls.URL_PATTERN.search(url)

    @classmethod
    def normalize_url(cls, url):
        m = cls.URL_PATTERN.findall(url)
        return m[0]

    def parse_lang(self):
        return None

    def parse_author(self):
        els = self.dom.select('.gh-header-meta a.author')
        if els:
            return els[0].get_text()

    def parse_publisher(self):
        return 'GitHub'

    def parse_pubdate(self):
        els = self.dom.select('.gh-header-meta [datetime]')
        if els:
            return to_datetime(els[0].get('datetime'))

    def parse_title(self):
        els = self.dom.select('.gh-header-title .js-issue-title')
        if els:
            return els[0].get_text()

    def parse_content(self):
        els = self.dom.select('td.markdown-body')
        return els[0]


class GithubBlobParser(Parser):
    NAME = 'github-blob'
    ALLOWED_DOMAINS = ['github.com']
    URL_PATTERN = re.compile(r'https://github\.com/.*?/blob/.*')

    @classmethod
    def check_url(cls, url):
        return cls.URL_PATTERN.search(url)

    @classmethod
    def normalize_url(cls, url):
        m = cls.URL_PATTERN.findall(url)
        href = m[0]
        href = href.split('?')[0]
        href = href.split('#')[0]
        return href

    def parse_lang(self):
        return None

    def parse_author(self):
        el = self.dom.find('span', attrs={'itemprop': 'author'})
        if el:
            return el.get_text()

    def parse_publisher(self):
        return 'GitHub'

    def parse_title(self):
        content = getattr(self, '_content', None)
        if content:
            el = get_first_child(content)
            if el.name in ['h1', 'h2', 'h3']:
                el.extract()
                return el.get_text()

        els = self.dom.select('div.breadcrumb')
        if els:
            return els[0].get_text()

    def parse_content(self):
        el = self.dom.find('article', attrs={'itemprop': 'text'})
        if el:
            self._content = el
            return el


class GistParser(Parser):
    NAME = 'github-gist'
    ALLOWED_DOMAINS = ['gist.github.com']
    URL_PATTERN = re.compile(r'gist\.github\.com/(?:(?:[^\/]+/.+)|\d+)')

    @classmethod
    def check_url(cls, url):
        return cls.URL_PATTERN.search(url)

    @property
    def dom(self):
        dom = getattr(self, '_dom', None)
        if dom is not None:
            return dom
        html = self.content.get('div')
        dom = BeautifulSoup(html, self.SOUP_FEATURES)
        self._dom = dom
        return self._dom

    def fetch(self):
        url = self.url
        if url.endswith('.js'):
            url += 'on'
        elif not url.endswith('.json'):
            url += '.json'
        req = self._request(url)
        self.content = req.json()
        self.url = url.replace('.json', '')

    def parse_lang(self):
        return None

    def parse_publisher(self):
        return 'Gist'

    def parse_author(self):
        return self.content.get('owner')

    def parse_pubdate(self):
        return to_datetime(self.content.get('created_at'))

    def parse_title(self):
        return self.content.get('description')

    def parse_content(self):
        html = parse_content_html(self.dom)
        dom = BeautifulSoup('<div>{0}</div>'.format(html), self.SOUP_FEATURES)
        return dom.find('div')


def expand_gist(content, parser):
    def fetch_gist_html(url):
        req = parser._request(url + '.json')
        content = req.json()
        html = content.get('div')
        dom = BeautifulSoup(html, LXML_GIST)
        return parse_content_html(dom)

    m = GIST_TAG.findall(content) or []
    for snippet in m:
        urls = GIST_URL.findall(snippet)
        if urls:
            try:
                repl = fetch_gist_html(urls[0])
                content = content.replace(snippet, repl)
            except RuntimeError:
                pass

    return content


def parse_content_html(dom):
    html = ''
    els = dom.find_all('div', attrs={'class': 'file'})
    for el in els:
        html += parse_file_html(el)
    return html


def parse_file_html(node):
    article = node.find('article')
    if article:
        return str(article)

    table = node.find('table')
    if not table:
        return ''

    blobs = table.select('td.blob-code')
    code = '\n'.join([blob.decode_contents() for blob in blobs])

    names = node.select('strong.gist-blob-name')
    if not names:
        return '<figure><pre>{0}</pre><figure>'.format(code)

    title = names[0].get_text()
    tpl = '<figure><pre>{0}</pre><figcaption>{1}</figcaption></figure>'
    return tpl.format(code, title.strip())
