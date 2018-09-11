import json
from .utils import to_datetime

ARTICLE_TYPES = (
    'Article', 'NewsArticle', 'Report',
    'ScholarlyArticle', 'SocialMediaPosting', 'TechArticle',
    'BlogPosting', 'MedicalScholarlyArticle',
)


def parse_ld_json(dom):
    els = dom.find_all('script', attrs={'type': 'application/ld+json'})
    if not els:
        return None

    schemas = []
    for el in els:
        text = el.get_text()
        start = text.find('{')
        end = text.rfind('}') + 1
        try:
            schema = json.loads(text[start:end])
            if schema.get('@type') in ARTICLE_TYPES:
                schemas.append(schema)
        except json.JSONDecodeError:
            pass

    if len(schemas) == 1:
        return schemas[0]


def parse_ld_title(schema):
    if not schema:
        return None
    return schema.get('name') or schema.get('headline')


def parse_ld_pubdate(schema):
    if not schema:
        return None
    return to_datetime(schema.get('datePublished'))


def parse_ld_author(schema):
    if not schema:
        return None
    return _normalize(schema.get('author'))


def parse_ld_publisher(schema):
    if not schema:
        return None
    return _normalize(schema.get('publisher'))


def parse_ld_image(schema):
    if not schema:
        return None

    image = schema.get('image')
    if not image:
        return None

    if isinstance(image, dict):
        src = image.get('url')
        if not src:
            return None

        rv = {'src': src}
        if 'width' in image:
            rv['width'] = image['width']
        if 'height' in image:
            rv['height'] = image['height']
        return rv

    return {'src': image}


def _normalize(data):
    if not data:
        return None

    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict):
        data = data.get('name')

    if isinstance(data, str):
        return data

    return None
