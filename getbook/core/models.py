import datetime
from collections import namedtuple


_Chapter = namedtuple(
    'Chapter',
    [
        'url', 'lang', 'image', 'publisher',
        'author', 'title', 'summary',
        'content', 'pubdate', 'attachments',
    ]
)

_Image = namedtuple('Image', ['uid', 'filepath', 'href', 'mimetype'])


class Image(_Image):
    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        return self.uid == other.uid


class Chapter(_Chapter):
    def to_dict(self):
        return self._asdict()


class Section(object):
    def __init__(self, title, subtitle=None):
        self.uid = None
        self.title = title
        self.subtitle = subtitle
        self.chapters = []


class Book(object):
    def __init__(self, uid, title, lang=None, author=None, pubdate=None):
        self.uid = uid
        self.title = title
        self.lang = lang

        if author is None:
            author = 'Doocer'
        self.author = author

        if pubdate is None:
            pubdate = datetime.datetime.utcnow()
        self.pubdate = pubdate

        self.cover = None
        self.sections = []
        self.chapters = []
        self.images = set()

    def add_section(self, section):
        section.uid = 's-{}'.format(len(self.sections) + 1)
        self.sections.append(section)
