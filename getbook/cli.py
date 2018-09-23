import os
import sys
import logging
import json
import datetime
from . import __version__ as version
from .core import Book, Section
from .gen import BookGen, filter_book_chapters


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
    config = {}
    if sys.platform == 'darwin':
        config = {
            "EBOOK_ENG_REGULAR_FONT": "Avenir.ttc",
            "EBOOK_ENG_BOLD_FONT": ("Avenir.ttc", 2),
            "EBOOK_CJK_REGULAR_FONT": ("PingFang.ttc", 2),
            "EBOOK_CJK_BOLD_FONT": ("PingFang.ttc", 8)
        }
    home_dir = os.path.expanduser('~')
    conf = os.path.join(home_dir, '.getbook/config.json')
    if os.path.isfile(conf):
        with open(conf) as f:
            config.update(json.load(f))
    return config


def parse_book_from_json(json_file, book_gen=None):
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

    for s in secs:
        if not isinstance(s, dict) and book_gen and s.startswith('http'):
            b = book_gen.parse(s, True)
            if isinstance(b, Book):
                subtitle = ''
                if b.author != 'Doocer':
                    subtitle = b.author
                section = Section(
                    title=b.title,
                    subtitle=subtitle,
                )
                section.chapters = b.chapters
                book.add_section(section)
            else:
                print('Invalid section source: {}'.format(s))
        else:
            section = Section(
                title=s['title'],
                subtitle=s.get('subtitle')
            )
            section.chapters = _format_chapters(s.get('chapters', []))
            book.add_section(section)

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
    parser.add_argument('--force', help='force fetching from network',
                        action='store_true')
    parser.add_argument('--days', help='only fetch chapters in days', type=int)
    args = parser.parse_args()

    if args.version:
        print('getbook v{}'.format(version))
        return

    if not args.url and not args.file:
        print('Please specify a file or URL')
        sys.exit(1)

    config_logging(args.verbose)
    config = load_config()
    # TODO: kindlegen
    bg = BookGen(config=config, kindlegen='kindlegen')

    if args.url:
        book = bg.parse(args.url, True)
    else:
        book = parse_book_from_json(args.file, bg)

    if not isinstance(book, Book):
        print('Invalid book URL')
        sys.exit(1)

    if args.cover:
        book.cover = args.cover

    if args.days:
        now = datetime.datetime.utcnow()
        start = now - datetime.timedelta(days=args.days)
        filter_book_chapters(book, start)
    bg.build(book, force=args.force)


if __name__ == '__main__':
    main()
