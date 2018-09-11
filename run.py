import sys
import time
from getbook.generator import Generator


def run(url):
    begin = time.time()
    g = Generator()
    d = g.parse(url)
    end = time.time()

    print(d['title'])
    print('------------')
    print('%(lang)s %(publisher)s %(author)s %(pubdate)s' % d)
    print('------------')
    print(d['attachments'])
    print('------------')
    print(d['content'])
    print('------------')
    print(end - begin)


run(sys.argv[1])
