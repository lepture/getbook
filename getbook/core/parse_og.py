from .utils import to_datetime

TITLES = [
    {'property': 'og:title'},
    {'name': 'twitter:title'},
    {'name': 'og:title'},
]

SUMMARIES = [
    {'property': 'og:description'},
    {'name': 'twitter:description'},
    {'name': 'og:description'},
    {'name': 'description'},
]

PUBDATES = [
    {'property': 'article:published_time'},
    {'name': 'article:published_time'},
]

IMAGE_SOURCES = [
    {'property': 'og:image'},
    {'name': 'twitter:image'},
    {'property': 'og:image:src'},
    {'name': 'twitter:image:src'},
    {'name': 'og:image:src'},
]

IMAGE_WIDTHS = [
    {'property': 'og:image:width'},
    {'name': 'twitter:image:width'},
    {'name': 'og:image:width'},
]

IMAGE_HEIGHTS = [
    {'property': 'og:image:height'},
    {'name': 'twitter:image:height'},
    {'name': 'og:image:height'},
]

IGNORE_IMAGES = ['apple-touch', 'avatar', 'logo', 'icon']


def get_meta_content(dom, attrs):
    for pair in attrs:
        el = dom.find('meta', attrs=pair)
        if el:
            return el.get('content')


def parse_og_title(dom):
    return get_meta_content(dom, TITLES)


def parse_og_summary(dom):
    return get_meta_content(dom, SUMMARIES)


def parse_og_pubdate(dom):
    return to_datetime(get_meta_content(dom, PUBDATES))


def parse_og_image(dom):
    src = get_meta_content(dom, IMAGE_SOURCES)
    if not src:
        return None

    if not src.startswith('http'):
        return None

    for key in IGNORE_IMAGES:
        if key in src:
            return None

    rv = {'src': src}

    width = get_meta_content(dom, IMAGE_WIDTHS)
    if width:
        rv['width'] = width

    height = get_meta_content(dom, IMAGE_HEIGHTS)
    if height:
        rv['height'] = height
    return rv
