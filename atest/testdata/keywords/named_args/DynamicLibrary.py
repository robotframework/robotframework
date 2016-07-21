#!/usr/bin/env python
# -*- coding: utf-8 -*-

from robot.utils import is_string

from helper import pretty


KEYWORDS = {
    'Escaped Default Value': ['d1=${notvariable}', 'd2=\\\\', 'd3=\n', 'd4=\t'],
    'Four Kw Args': ['a=default', 'b=default', 'c=default', 'd=default'],
    'Mandatory, Named And Varargs': ['a', 'b=default', '*varargs'],
    'Mandatory And Kwargs': ['man1', 'man2', 'kwarg=KWARG VALUE'],
    'Mandatory And Named': ['a', 'b=default'],
    'Named Arguments With Varargs': ['a=default', 'b=default', '*varargs'],
    'One Kwarg Returned': ['kwarg='],
    'Two Kwargs': ['first=', 'second='],
    u'Nön äscii named args': [u'nönäscii=', u'官话='],
    'three named': ['a=a', 'b=b', 'c=c']
}


class DynamicLibrary(object):

    def __init__(self, **extra):
        self.keywords = dict(KEYWORDS, **extra)

    def get_keyword_names(self):
        return self.keywords.keys()

    def run_keyword(self, kw_name, args):
        return self._pretty(*args)

    def _pretty(self, *args, **kwargs):
        if all(is_string(a) for a in args):
            return pretty(*args, **kwargs)
        return args[0] if len(args) == 1 else args

    def get_keyword_arguments(self, kw_name):
        return self.keywords[kw_name]
