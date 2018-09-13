# coding: utf-8

import re
import time
import hashlib
import dateutil.parser
from datetime import datetime, date
from urllib.parse import urlparse

USELESS_TEXT = re.compile(r'[\d|<>()\[\]\-：:【】●]')
USELESS_IDENTS = [
    'col-', 'offset', 'pull-',
    '-sm-', '-xs-', '-md-', '-lg-', '-xl-',
]
UTM_QUERY = re.compile(r'utm_\w+=[^&]+&?')
REF_QUERY = re.compile(r'(?:source|ref|refer)=[^&]+&?')


def to_datetime(value):
    if not value:
        return None
    if len(value) < 7:
        return None
    value = value.strip()
    if value.startswith('(') and value.endswith(')'):
        value = value[1:-1]
    try:
        date = dateutil.parser.parse(value)
        if not date:
            return None
        return datetime.fromtimestamp(time.mktime(date.utctimetuple()))
    except:
        return None


def get_depth(node):
    return len(list(node.parents))


def pure_text(node):
    if isinstance(node, str):
        text = node
    else:
        text = node.get_text(strip=True)
    text = re.sub(r'\s', '', text)
    text = USELESS_TEXT.sub('', text)
    return text


def match_specific_symbols(ident, symbols):
    if not ident:
        return False
    ident = ' '.join(ident)
    for s in symbols:
        if s in ident:
            return True
    return False


def normalize_url(url):
    url = url.strip()
    url = url.split('#')[0]

    if not re.match(r'^https?:\/\/', url):
        url = 'http://%s' % url

    parsed = urlparse(url)

    if parsed.query:
        query = UTM_QUERY.sub('', parsed.query)
        query = REF_QUERY.sub('', query)
        url = '{}://{}{}?{}'.format(
            parsed.scheme,
            parsed.hostname,
            parsed.path,
            query
        )

    # remove ? at the end of url
    url = re.sub(r'\?$', '', url)
    return url


def get_canonical_link(dom):
    el = dom.find('link', attrs={'rel': 'canonical'})
    if el:
        href = el.get('href')
        if href and href.startswith('http'):
            return href


def get_first_child(node):
    for el in node.contents:
        if getattr(el, 'name', None):
            return el


def identities(node):
    tokens = []
    ident = node.get('id')
    if ident:
        tokens.append(ident)
    tokens.extend(node.get('class', []))
    return [i.lower() for i in tokens if _is_valid_ident(i)]


def sha1name(name):
    if not isinstance(name, bytes):
        name = name.encode('utf-8')
    return hashlib.sha1(name).hexdigest()


def format_date(value, format='%Y-%m-%d'):
    if isinstance(value, (datetime, date)):
        return value.strftime(format=format)

    rv = dateutil.parser.parse(value)
    if rv:
        return rv.strftime(format=format)
    return ''


def _is_valid_ident(ident):
    ident = ident.lower()
    for k in USELESS_IDENTS:
        if k in ident:
            return False
    return True
