from collections import namedtuple


Chapter = namedtuple(
    'Chapter',
    [
        'url', 'lang', 'image', 'publisher',
        'author', 'title', 'summary',
        'content', 'pubdate', 'attachments',
    ]
)


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
