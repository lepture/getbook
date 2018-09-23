import os
from jinja2 import Environment, FileSystemLoader
from ..core.utils import format_date

_CWD = os.path.dirname(os.path.abspath(__file__))


def create_jinja():
    loaders = [os.path.join(_CWD, 'templates')]
    jinja = Environment(
        loader=FileSystemLoader(loaders),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        extensions=[
            'jinja2.ext.do',
            'jinja2.ext.loopcontrols',
            'jinja2.ext.with_',
        ]
    )
    jinja.filters.update({
        'date': format_date,
        'chapter_count': chapter_count,
    })
    return jinja


def chapter_count(book):
    if not book.sections:
        return len(book.chapters)

    count = 0
    for s in book.sections:
        count += len(s.chapters)
    return count
