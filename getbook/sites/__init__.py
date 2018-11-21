# coding: utf-8

import pkg_resources
from urllib.parse import urlparse
from collections import defaultdict
from .github import GistParser, GithubIssueParser, GithubBlobParser
from .feed import FeedParser

__all__ = ['get_parser_by_url', 'get_parser_by_html']


URL_PRESET = []
DOMAIN_URL_PRESET = defaultdict(list)
HTML_PRESET = []


def register(Parser):
    if hasattr(Parser, 'ALLOWED_DOMAINS'):
        for host in Parser.ALLOWED_DOMAINS:
            DOMAIN_URL_PRESET[host].append((Parser.check_url, Parser))
    else:
        if hasattr(Parser, 'check_url'):
            URL_PRESET.append((Parser.check_url, Parser))

    if hasattr(Parser, 'check_html'):
        HTML_PRESET.append((Parser.check_html, Parser))


register(GistParser)
register(GithubIssueParser)
register(GithubBlobParser)
register(FeedParser)

for pkg in pkg_resources.iter_entry_points('getbook.parsers'):
    register(pkg.load())


def get_parser_by_url(url):
    host = urlparse(url).hostname
    preset = DOMAIN_URL_PRESET.get(host, URL_PRESET)
    return _get_parser(url, preset)


def get_parser_by_html(html):
    return _get_parser(html, HTML_PRESET)


def _get_parser(param, preset):
    for fn, parser in preset:
        if fn(param):
            return parser
