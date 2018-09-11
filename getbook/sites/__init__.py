# coding: utf-8

from .github import GistParser, GithubIssueParser, GithubBlobParser

__all__ = ['get_parser_by_url', 'get_parser_by_html']


url_preset = []
html_preset = []


def register(Parser):
    pattern = getattr(Parser, 'URL_PATTERN', None)
    if pattern:
        url_preset.append((pattern.search, Parser))

    if hasattr(Parser, 'match_html'):
        html_preset.append((Parser.match_html, Parser))


register(GistParser)
register(GithubIssueParser)
register(GithubBlobParser)


def get_parser_by_url(url):
    return _get_parser(url, url_preset)


def get_parser_by_html(html):
    return _get_parser(html, html_preset)


def _get_parser(param, preset):
    for fn, parser in preset:
        if fn(param):
            return parser
