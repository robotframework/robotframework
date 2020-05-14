# -*- coding: utf-8 -*-

from helper import pretty


KEYWORDS = {
    'One Arg': ['arg'],
    'Two Args': ['first', 'second'],
    'Four Args': ['a=1', ('b', '2'), ('c', 3), ('d', 4)],
    'Defaults w/ Specials': ['a=${notvar}', 'b=\n', 'c=\\n', 'd=\\'],
    'Args & Varargs': ['a', 'b=default', '*varargs'],
    u'Nön-ÄSCII names': [u'nönäscii', u'官话'],
}


class DynamicWithoutKwargs(object):

    def __init__(self, **extra):
        self.keywords = dict(KEYWORDS, **extra)

    def get_keyword_names(self):
        return self.keywords.keys()

    def run_keyword(self, kw_name, args):
        return self._pretty(*args)

    def _pretty(self, *args, **kwargs):
        return pretty(*args, **kwargs)

    def get_keyword_arguments(self, kw_name):
        return self.keywords[kw_name]
