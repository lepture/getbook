# coding: utf-8

import re

from .utils import pure_text, identities, match_specific_symbols
from . import config

h_tag = re.compile(r'^h\d$')


def preclean(node):
    for el in node.find_all(True):
        clean_node(el)


def clean_node(node):
    clean_ignored(node)
    if not node:
        return

    if node.name in config.block_element_tags:
        return clean_block(node)

    if node.name in config.media_element_tags:
        clean_media(node)
        return

    if node.name == 'picture':
        clean_picture(node)
        return

    if node.name == 'a':
        clean_link(node)
        return

    if node.name == 'img':
        clean_image(node)
        return

    if node.name == 'span':
        return clean_span(node)

    if node.name == 'wbr':
        node.unwrap()
        return

    return node


def clean_ignored(node):
    # related articles after content
    tag = getattr(node, 'name', None)
    if not tag:
        return

    if tag in ['p', 'div', 'ul', 'ol'] or h_tag.search(tag):
        if _is_related_after(node):
            return node.extract()

    ident = identities(node)
    # when there are too many class, be careful
    if len(ident) > 5:
        return

    for key in ident:
        for symbol in config.force_keep_symbols:
            if symbol in key:
                return

        for symbol in config.ignored_symbols:
            if symbol in key:
                return node.extract()

        for symbol in config.ignored_prefix_symbols:
            if key.startswith(symbol):
                return node.extract()

        for symbol in config.ignored_suffix_symbols:
            if key.endswith(symbol):
                return node.extract()

        for symbol in config.ignored_in_content:
            if symbol in key:
                return node.extract()

    links = node.find_all('a')
    link_text = ''.join([pure_text(a) for a in links])
    if len(pure_text(node)) - len(link_text) > config.min_negative_text_length:
        return

    if match_specific_symbols(ident, config.negative_symbols):
        return node.extract()


def clean_block(node):
    style = node.get('style')
    if style and re.search(r'display:\s*none', style):
        node.extract()
        return

    ident = identities(node)
    if match_specific_symbols(ident, ['title']):
        return node

    links = node.find_all('a')
    link_text = ''.join([pure_text(a) for a in links])
    link_text_length = len(link_text)
    text_length = len(pure_text(node))
    images = node.find_all(config.media_element_tags)
    if images:
        if node.name == 'table' and not text_length and len(images) == 1:
            node = node.replace_with(images[0])

        delta = text_length - link_text_length
        if delta > 20 * len(images):
            return

        for img in images:
            _load_lazy_img(img)

        return node

    # less than 2 links is not rubbish content
    if len(links) < 2:
        return node

    if text_length - link_text_length > config.min_length_of_paragraph:
        return node

    # it may contain title
    if node.find_all(['h1', 'h2']):
        return node

    if node.name in ['ul', 'ol']:
        ident = identities(node)
        li = node.find('li')
        if li:
            ident.extend(identities(li))

        if not ident:
            return node

    node.extract()


def clean_picture(node):
    img = node.find('img')
    if img:
        clean_image(img)
    if img:
        node.replace_with(img)


def clean_span(node):
    ident = identities(node)
    for c in ident:
        if '-' in c:
            return node
        if len(c) > config.max_length_of_class:
            node.extract()
            return


def clean_media(node):
    src = node.get('src')
    if not src:
        return node.extract()

    for key in config.positive_sources:
        if key in src:
            return False

    node.extract()


def clean_link(node):
    src = node.get('href', '')

    for key in config.negative_sources:
        if key in src:
            return node.extract()


def clean_image(node):
    _load_lazy_img(node)
    src = node.get('src')

    if not src:
        srcset = node.get('srcset')

        if srcset:
            src = srcset.split(' ')[0]
            node['src'] = src

    if not src or src.startswith('data:'):
        node.extract()


def _is_related_after(node):
    text = pure_text(node).lower()
    if len(text) > 20:
        return False

    for word in config.related_content_text:
        if word in text:
            return len(text) / len(word) < 3

    return False


def _load_lazy_img(node):
    src = _get_lazy_img_src(node)
    if not src and node.parent:
        src = _get_lazy_img_src(node.parent)
    if src:
        node['src'] = src


def _get_lazy_img_src(node):
    for key in config.img_lazy_srcs:
        src = node.get(key, None)
        if src:
            return src
