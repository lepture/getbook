# coding: utf-8

import re

from .utils import to_datetime, get_first_child
from .parse_content import guess_content
from .parse_title import guess_title
from .parse_lang import (
    parse_lang_by_dom,
    parse_lang_by_text,
)
from .parse_og import (
    parse_og_title,
    parse_og_summary,
    parse_og_image,
    parse_og_pubdate,
)
from .parse_schema import (
    parse_ld_json,
    parse_ld_title,
    parse_ld_author,
    parse_ld_pubdate,
    parse_ld_publisher,
    parse_ld_image,
)
from .core_parser import Parser
from .pre_clean import preclean

GIST_URL = re.compile(r'https://gist\.github\.com/(?:(?:[^\/]+/.+)|\d+)\.js')


class FallbackParser(Parser):
    NAME = 'fallback'
    AUTHOR_PATTERN = re.compile(r'(?:作者|:|：|by\s)', re.I | re.U)
    OTHER_TITLES = (
        'a[rel="bookmark"]', '.entry-title', '.article-title', '.title',
        '.tit', '.Title', '.titName', '.heading', '.headline', '#headline',
        '.js-issue-title', '#title',
    )
    AUTHORS = (
        '.hentry .vcard .fn', '[itemprop="author"]',
        '.author .fn', 'a[rel=author]', '.entry-author',
        '#author', '.author',
    )
    PUBDATES = (
        '.updated', '[itemprop="datePublished"]',
        '.created', 'time[pubdate]', '.published',
        '.time', '#datetime', 'time[datetime]', '.pubTime',
    )
    CONTENTS = (
        '.hentry .entry-content',
    )

    def before_parse(self):
        super(FallbackParser, self).before_parse()
        self.schema = parse_ld_json(self.dom)

        # support for gist
        for script in self.dom.find_all('script'):
            src = script.get('src')
            if src and GIST_URL.search(src):
                div = self.create_attachment_tag('gist', src[:-3])
                script.replace_with(div)

    def get_user_agent(self, url):
        if url.startswith('https://t.co'):
            return 'curl'
        return self.USER_AGENT

    def parse_lang(self):
        title = self.parse_title()
        lang = parse_lang_by_text(title) or parse_lang_by_dom(self.dom)
        return lang or 'en'

    def parse_publisher(self):
        publisher = parse_ld_publisher(self.schema)
        if publisher:
            return publisher

        node = self.dom.find('meta', attrs={'property': 'og:site_name'})
        if node:
            return node.get('content')

    def parse_title(self):
        title = getattr(self, '_title', None)
        if title:
            return title

        title = self.parse_possible_title()
        self._title = title
        return title

    def parse_content(self):
        for node in self.select_by_rules(self.CONTENTS):
            if node:
                preclean(node)
                self._content = node
                return node

        preclean(self.dom)
        self._content = guess_content(self.dom)
        return self._content

    def parse_author(self):
        author = parse_ld_author(self.schema)
        if author:
            return author

        for el in self.select_by_rules(self.AUTHORS):
            text = str(el)
            if '>' in text:
                continue
            text = self.AUTHOR_PATTERN.sub('', text).strip()
            if len(text) > 48:
                continue
            el.extract()
            return text

        el = self.dom.find('meta', attrs={'name': 'author'})
        if el:
            return el.get('content')

        # use twitter creator as author name
        el = self.dom.find('meta', attrs={'name': 'twitter:creator'})
        if el:
            text = el.get('content', '')
            return text.replace('@', '')

    def parse_pubdate(self):
        pubdate = parse_ld_pubdate(self.schema) or parse_og_pubdate(self.dom)
        if pubdate:
            return pubdate

        for node in self.select_by_rules(self.PUBDATES):
            date = to_datetime(node.get('datetime'))
            if date:
                node.extract()
                return date

            text = node.get('title') or node.get_text()
            if text:
                date = to_datetime(text)
                if date:
                    node.extract()
                    return date

        el = self.dom.find('meta', attrs={'name': 'pubdate'})
        if el:
            return to_datetime(el.get('content'))

    def parse_image(self):
        return parse_ld_image(self.schema) or parse_og_image(self.dom)

    def parse_summary(self):
        return parse_og_summary(self.dom)

    def parse_possible_title(self):
        content = getattr(self, '_content', None)
        if content:
            node = get_first_child(content)
            if node.name == 'h1':
                title = node.get_text()
                node.extract()
                return title

        doc = self.dom.find('title')
        if not doc:
            return 'Untitled'

        doctitle = doc.get_text()

        els = self.dom.select('.hentry .entry-title')
        if els and len(els) == 1:
            node = els[0]
            title = node.get_text()
            node.extract()
            return title

        # find absolute link title
        rules = ['h1 a', 'h2 a', 'h3 a']
        for rule in rules:
            for el in self.dom.select(rule):
                href = el.get('href')
                if href and self.urljoin(href) == self.url:
                    el.extract()
                    return el.get_text()

        possible_titles = []
        for rule in self.OTHER_TITLES:
            possible_titles.extend(self.dom.select(rule))

        title = guess_title(possible_titles, doctitle, self.url)
        if title:
            return title

        possible_titles = self.dom.find_all(['h2', 'h3', 'h1'])
        title = guess_title(possible_titles, doctitle, self.url)
        if title:
            return title

        title = parse_ld_title(self.schema) or parse_og_title(self.dom)
        if title:
            return title
        return doctitle
