import sys
import time
from getbook.parser import Readable


def run(url):
    begin = time.time()
    parser = Readable(url)
    d = parser.parse(True)
    end = time.time()

    print(d.title)
    print('------------')
    print('%s %s %s %s' % (d.lang, d.publisher, d.author, d.pubdate))
    print('------------')
    print(d.attachments)
    print('------------')
    print(d.content)
    print('------------')
    print(end - begin)


run(sys.argv[1])
