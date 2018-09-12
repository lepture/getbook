# coding: utf-8

import json
import re
from collections import defaultdict

from .utils import pure_text, identities, match_specific_symbols
from . import config

CJK_NEWLINE = re.compile(r'([\u4e00-\u9fff]+?)\n([\u4e00-\u9fff+?])')
MANY_BR = re.compile(r'(<br\s*/?>\s*\n*){3,}')


def parse_content_and_attachments(node, soup):
    attachments = parse_attachments(node, soup)
    content = normalize_html(node)
    return content, attachments


def parse_attachments(node, soup):
    attachments = defaultdict(list)

    for el in node.find_all(config.source_element_tags):
        data = parse_attachment(el, soup)
        if data:
            attachments[el.name].append(data)

    for el in node.select('[data-attachment]'):
        data = parse_attachment(el)
        if data:
            tag = el.get('data-attachment')
            attachments[tag].append(data)

    for el in node.find_all(True):
        clean_node(el)

    return attachments


def parse_attachment(node, soup=None):
    if soup is None:
        tag = node.get('data-attachment')
        data = {'tag': tag}
        for k in node.attrs:
            if k.startswith('data-'):
                data[k.replace('data-', '')] = node.get(k)
        return data

    tag = node.name
    attrs = config.elements_keep_attributes[tag]
    data = {k: node.get(k) for k in attrs if node.get(k)}

    data['tag'] = tag

    if tag in ('audio', 'video'):
        sources = _get_child_attchments(node, 'source')
        if sources:
            data['sources'] = sources
        tracks = _get_child_attchments(node, 'track')
        if tracks:
            data['tracks'] = tracks
    elif tag == 'object':
        params = _get_child_attchments(node, 'param')
        if params:
            data['params'] = params

    if tag in config.source_element_tags:
        if not data.get('src') and not data.get('sources'):
            node.extract()
            return None

    src = data.get('src')
    if src and src.startswith('//'):
        data['src'] = 'http:' + src

    # replace source_element_tags
    span = soup.new_tag('span')
    span['class'] = 'tag tag-' + tag
    span['data-attrs'] = json.dumps(data)
    span.string = tag
    node.replace_with(span)
    return data


def normalize_html(node):
    tag = getattr(node, 'name', None)

    if tag is None:
        return ''

    if tag and tag in config.content_container_tags:
        html = ''.join([str(el) for el in node.contents])
    else:
        html = str(node)

    html = CJK_NEWLINE.sub(r'\1\2', html)
    return transform_newlines(html)


def clean_node(node):
    if is_blank_element(node):
        node.extract()
        return

    if is_ignored_elements(node):
        node.extract()
        return

    if node.name == 'table':
        table_codeblock(node)
    elif node.name == 'a':
        href = node.get('href', '')
        if href == '#' or href.lower().startswith('javascript:'):
            node.name = 'span'

    if node:
        unwrap_useless_tag(node)

    if node:
        clean_mess(node)
    return node


def is_blank_element(node):
    if node.name in config.self_closing_tags:
        return False

    if node.name in ['td', 'th']:
        return False

    if node.find(config.self_closing_tags):
        return False

    if node.get_text():
        return False

    return not node.find(src=True)


def is_ignored_elements(node):
    ident = identities(node)

    if match_specific_symbols(ident, config.ignored_bottom_symbols):
        for item in node.find_all_next(True):
            item.extract()
        return True

    if match_specific_symbols(ident, config.ignored_meta_symbols):
        return True

    if not match_specific_symbols(ident, config.negative_symbols):
        return False

    return len(pure_text(node)) < config.min_negative_text_length


def unwrap_useless_tag(node):
    tag = getattr(node, 'name', None)
    if tag and tag in config.useless_tags:
        return node.unwrap()

    # unwrap useless span
    if tag == 'span':
        if node.get('class'):
            return

        p = node.parent
        # clean span in paragraph
        if p and p.name == 'p':
            return node.unwrap()


def clean_mess(node):
    tag = getattr(node, 'name', None)
    if not tag:
        return

    if tag == 'span' and node.get('class'):
        if 'tag' in node.get('class'):
            return

        p = node.parent
        if p and p.name in ['pre', 'code']:
            return

    keep_attributes = config.elements_keep_attributes.get(tag, [])
    attrs = list(node.attrs.keys())

    for attr in attrs:
        if attr in config.keep_attributes:
            continue
        if attr not in keep_attributes:
            del node.attrs[attr]


def table_codeblock(node):
    tds = node.find_all('td')
    if len(tds) != 2:
        return
    line_td = tds[0]
    text = line_td.get_text(strip=True)
    if not text.startswith('123'):
        return
    code = tds[1]
    code.name = 'pre'
    node.replace_with(code)
    return code


def transform_newlines(html):
    html = MANY_BR.sub('<br/><br/>', html)

    # transform br to paragraph
    split_key = '<br/><br/>'
    if split_key in html and '</p>' not in html:
        bits = html.split(split_key)
        html = '\n'.join(['<p>%s</p>' % s for s in bits])
    return html.strip()


def _get_child_attchments(node, tag):
    els = node.find_all(tag)
    if els:
        data = []
        attrs = config.elements_keep_attributes[tag]
        for el in els:
            data.append({k: el.get(k) for k in attrs if el.get(k)})
        return data
