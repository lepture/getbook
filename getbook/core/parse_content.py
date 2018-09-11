# coding: utf-8

import math
from .utils import pure_text, identities, get_depth
from . import config


def guess_content(dom):
    candidates = find_candidates(dom)
    if not candidates:
        return None
    chain = create_candidate_chain(candidates)
    target = find_target(chain)
    return target[0]


def find_candidates(dom):
    tags = list(config.content_container_tags)
    if len(dom.select('body > p')) > 5:
        tags.append('body')

    candidates = []

    for el in dom.find_all(tags):
        cand = create_candidate(el)
        if cand:
            candidates.append(cand)

    return candidates


def create_candidate(el):
    depth = get_depth(el)
    if depth > config.max_depth_of_candidate:
        return

    if len(pure_text(el)) < config.min_content_length:
        return

    is_possible = el.find_all(config.source_element_tags)
    # <td> tag should not contain <table>
    # otherwise, it should be layout
    if is_possible and el.name == 'td':
        tag = getattr(el.contents[0], 'name', None)
        if tag and tag == 'table':
            return

    point = cal_point(el, depth)
    return el, depth, point


def create_candidate_chain(candidates):
    top = sorted(candidates, key=lambda o: o[2], reverse=True)[0]
    min_point = max(math.sqrt(top[2]), top[2] / 4)
    candidates.sort(key=lambda o: o[1])

    chain = []
    children = []

    for cand in candidates:
        if cand[2] < min_point:
            continue
        if is_parent(cand[0], top[0]):
            chain.append(cand)
        elif is_parent(top[0], cand[0]):
            if children:
                latest = children[-1]
                if latest[1] == cand[1]:
                    # TODO
                    if latest[2] > cand[2]:
                        continue
                    children.pop()
                    children.append(cand)
                elif is_parent(latest[0], cand[0]):
                    children.append(cand)
            else:
                children.append(cand)

    chain.append(top)
    chain.extend(children)
    return chain


def find_target(chain):
    count = len(chain)
    if count == 1:
        return chain[0]

    targets = []
    last_item = chain[-1]

    for index, item in enumerate(chain[:-1]):
        diff = item[2] - chain[index + 1][2]
        if diff < config.min_diff_of_point:
            continue
        targets.append((diff, item))

    if not targets:
        return last_item

    target = sorted(targets, key=lambda o: o[0], reverse=True)[0]
    current = target[1]

    # it maybe the last one
    if current[2] - last_item[2] < (last_item[1] - current[1]) ** 2:
        return last_item

    # TODO
    return current


def is_parent(parent, child):
    count = 0
    while count < 5 and child is not None:
        p = child.parent
        if p == parent:
            return True
        child = p
        count += 1
    return False


def cal_point(el, depth):
    mul = depth
    idc = ' '.join(identities(el))
    for word in config.positive_symbols:
        if word in idc:
            mul += 0.6
            break

    for word in config.negative_symbols:
        if word in idc:
            mul -= 0.5
            break

    # plus paragraph point
    p_count = len(el.select('> p'))
    if p_count:
        mul += math.sqrt(depth) / 5

    link_text = ''.join([pure_text(a) for a in el.find_all('a')])
    valid_text_length = len(pure_text(el)) - len(link_text)

    aside = el.find('aside')
    if aside:
        valid_text_length -= len(pure_text(aside)) / 2

    point = valid_text_length / config.min_length_of_paragraph
    return mul * point
