from .core import Parser


class KanunuParser(Parser):
    NAME = 'kanunu'
    ALLOWED_DOMAINS = ['www.kanunu8.com']

    @classmethod
    def check_url(cls, url):
        return

    def is_index(self):
        pass

    def is_chapter(self):
        pass

    def parse_index(self):
        pass

    def parse_chapter(self):
        pass
