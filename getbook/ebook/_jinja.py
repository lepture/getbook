import os
import datetime
import dateutil
from jinja2 import Environment, FileSystemLoader

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
    })
    return jinja


def format_date(value, format='%Y-%m-%d'):
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.strftime(format=format)

    rv = dateutil.parser.parse(value)
    if rv:
        return rv.strftime(format=format)
    return ''
