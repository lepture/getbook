# https://www.w3.org/International/questions/qa-http-and-lang

import re

CJK = re.compile(r'[\u2E80-\u9FFF]')
JP = re.compile(r'[\u3040-\u31FF]')
KO = re.compile(r'[\u3130-\u318F]')


def parse_lang_by_dom(dom):
    node = dom.find('html')
    if not node:
        return None

    lang = node.get('lang') or node.get('xml:lang')
    if lang:
        return lang.split('-')[0]

    for el in node.find_all('meta', attrs={'http-equiv': True}):
        equiv = el.get('http-equiv')
        if equiv and equiv.lower() == 'content-language':
            lang = el.get('content')
            if not lang:
                return None
            # <meta http-equiv="Content-Language" content="de, fr, it">
            lang = lang.split(',')[0]
            return lang.split('-')[0]

    return None


def parse_lang_by_text(text):
    if JP.search(text):
        return 'ja'
    if KO.search(text):
        return 'kr'
    if CJK.search(text):
        return 'zh'
    return None
