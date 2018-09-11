# coding: utf-8

import re
from urllib.parse import urljoin
from .utils import identities, get_depth

SPLIT_PATTERN = re.compile(r'[-—–_|<>«»‹›·]', re.U)


def guess_title(candidates, doctitle, url):
    cache = []
    doctitles = SPLIT_PATTERN.split(doctitle)
    for node in candidates:
        if node.name == 'a':
            title = guess_from_a_tag(node, doctitle, url)
            if title:
                return title
        else:
            link_node = node.find('a')
            if link_node:
                title = guess_from_a_tag(link_node, doctitle, url)
                if title:
                    return title
                continue

        guess = guess_from_doctitles(node.get_text(), doctitles)
        if guess:
            right = sorted(guess, key=lambda o: o[0], reverse=True)[0]
            point = 0.3
            if node.name not in ('header', 'h1', 'h2', 'h3', 'a'):
                point = 0.5

            ident = ''.join(identities(node))
            if right[0] > point and 'title' in ident:
                node.extract()
                return right[1]

            if right[0] > point:
                cache.append((node, right[0], right[1]))

    if not cache:
        return None

    cache = sorted(
        cache,
        key=lambda o: get_depth(o[0]) * o[1],
        reverse=True
    )
    node = cache[0][0]
    title = node.get_text()
    for span in node.find_all('span'):
        span.extract()

    title = node.get_text() or title
    if not title:
        return None

    node.extract()
    for t in doctitles:
        if 1 - levenshtein(t, title) / float(len(title)) > 0.9:
            return t.strip()
    return title.strip()


def guess_from_a_tag(node, doctitle, url):
    alt_title = node.get_text()
    title = node.get('title') or alt_title
    # people using img as title
    img = node.find('img')
    if img and img.get('alt'):
        title = img.get('alt')

    href = node.get('href')
    if same_link(href, url) and len(title) <= len(doctitle)\
       and is_similar(title, doctitle):
        node.extract()
        if alt_title in title:
            # title has other description
            return alt_title
        return title


def guess_from_doctitles(title, doctitles):
    cache = []
    for t in doctitles:
        t = t.strip()
        point = similarity_point(t, title)
        cache.append((point, t))
    return cache


def same_link(a, b):
    a = urljoin(a, b)
    if not a or not b:
        return False
    if a == b:
        return True
    if a.rstrip('/') == b.rstrip('/'):
        return True
    return False


def is_similar(title, doctitle):
    if title in doctitle:
        return True
    return similarity_point(title, doctitle) > 0.3


def similarity_point(a, b):
    a = a.strip()
    b = b.strip()
    max_length = max(len(a), len(b))
    min_length = min(len(a), len(b))
    if max_length >= 3 * min_length:
        return 0
    return 1 - levenshtein(a, b) / float(max_length)


def levenshtein(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]
