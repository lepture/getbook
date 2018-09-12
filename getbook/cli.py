import os
import logging
import json
from . import __version__ as version
from .core import Book, Section
from .gen import BookGen


def config_logging(verbose=False):
    # TODO
    logger = logging.getLogger('getbook')
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger.addHandler(handler)


def load_config():
    home_dir = os.path.expanduser('~')
    conf = os.path.join(home_dir, '.getbook/config.json')
    if os.path.isfile(conf):
        with open(conf) as f:
            return json.load(f)


def parse_book_from_json(json_file):
    with open(json_file) as f:
        data = json.load(f)

    def _format_chapters(chapters):
        rv = []
        for ch in chapters:
            if isinstance(ch, dict):
                rv.append(ch)
            else:
                rv.append({'url': ch})
        return rv

    keys = ['uid', 'title', 'lang', 'author', 'pubdate']
    book = Book(**{k: data.get(k) for k in keys})
    book.cover = data.get('cover')

    chapters = data.get('chapters', [])
    secs = data.get('sections', [])
    if not secs:
        book.chapters = _format_chapters(chapters)
        return book

    for i, s in enumerate(secs):
        section = Section(
            uid='s-{}'.format(i),
            title=s['title'],
            subtitle=s.get('subtitle')
        )
        section.chapters = _format_chapters(s.get('chapters', []))
        book.sections.append(section)

    return book


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', help='print getbook version',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='print debug log',
                        action='store_true')
    parser.add_argument('-f', '--file', help='create book via JSON file')
    parser.add_argument('-u', '--url', help='create book via URL')
    parser.add_argument('-c', '--cover', help='add book cover URL')
    args = parser.parse_args()

    if args.version:
        print('getbook v{}'.format(version))
        return

    config_logging(args.verbose)
    config = load_config()
    # TODO: kindlegen
    bg = BookGen(config=config, kindlegen='kindlegen')
    if args.url:
        book = bg.parse(args.url, True)
        if not isinstance(book, Book):
            print('Invalid book URL')
        else:
            if args.cover:
                book.cover = args.cover
            bg.build(book)
    elif args.file:
        book = parse_book_from_json(args.file)
        if args.cover:
            book.cover = args.cover
        bg.build(book)
    else:
        print('Please specify a file or URL')


if __name__ == '__main__':
    main()
