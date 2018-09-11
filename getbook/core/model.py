from collections import namedtuple


_Chapter = namedtuple(
    'Chapter',
    [
        'url', 'lang', 'image', 'publisher',
        'author', 'title', 'summary',
        'content', 'pubdate', 'attachments',
    ]
)


class Chapter(_Chapter):
    def to_dict(self):
        return self._asdict()


class Section(object):
    def __init__(self, uid, title, subtitle=None):
        self.uid = uid
        self.title = title
        self.subtitle = subtitle
        self.chapters = []


class Book(object):
    def __init__(self, uid, title, lang=None, author=None):
        self.uid = uid
        self.title = title
        self.lang = lang
        self.author = author or 'Doocer'
        self.sections = []
        self.chapters = []
        self.images = []
