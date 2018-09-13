# coding: utf-8

import logging
from .core import Chapter, FallbackParser
from .sites import get_parser_by_url, get_parser_by_html
from .sites.github import expand_gist

log = logging.getLogger(__name__)


class Readable(object):
    def __init__(self, url, html=None):
        Parser = get_parser_by_url(url)
        if Parser:
            url = Parser.normalize_url(url)
            self._parser = Parser(url, html)
        else:
            url = FallbackParser.normalize_url(url)

        self.url = url
        self.html = html

    def get_parser(self):
        parser = getattr(self, '_parser', None)
        if parser:
            return parser

        if self.html:
            Parser = get_parser_by_html(self.html) or FallbackParser
            self._parser = Parser(self.url, self.html)

            return self._parser

        p = FallbackParser(self.url)
        p.fetch()

        self.html = p.content

        Parser = get_parser_by_html(self.html)
        if Parser:
            self.url = p.url
            self._parser = Parser(self.url, self.html)
        else:
            self._parser = p

        return self._parser

    def parse(self, expand=False):
        parser = self.get_parser()
        log.debug('Parser: {}'.format(parser.NAME))
        chapter = parser.parse()
        if expand and isinstance(chapter, Chapter):
            chapter = self.expand(chapter)
        return chapter

    def expand(self, chapter):
        if not chapter.attachments or 'gist' not in chapter.attachments:
            return chapter

        content = expand_gist(chapter.content, self.get_parser())
        data = dict(chapter.to_dict())
        data['content'] = content
        return Chapter(**data)
