import re


def add_toc(doc):
    if re.search(r'^\%TABLE_OF_CONTENTS\%$', doc, re.MULTILINE):
        headings = _get_headings(doc)
        toc = _create_toc(headings)
        doc = doc.replace('%TABLE_OF_CONTENTS%', '\n'.join(toc))
    return doc


def _get_headings(doc):
    match = re.findall(r'(^= )(.*)( =$)', doc, re.MULTILINE)
    return ['- `%s`' % heading[1] for heading in match]


def _create_toc(headings):
    toc = ['== Table of contents ==', '']
    toc.extend(headings)
    toc.extend(['- `Importing`', '- `Shortcuts`', '- `Keywords`'])
    return toc
