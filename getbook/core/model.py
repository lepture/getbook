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
    def __init__(self, title):
        self.title = title
        self.chapters = []


class Book(object):
    def __init__(self, title, lang=None, author=None):
        self.title = title
        self.lang = lang
        self.author = author
        self.sections = []
        self.chapters = []
