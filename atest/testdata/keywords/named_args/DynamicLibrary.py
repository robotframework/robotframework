#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dynamic_library_impl import (mandatory_and_kwargs, mandatory_and_named, mandatory_named_and_varargs, one_kwarg,
                                 two_kwargs, four_kw_args, named_arguments_with_varargs, escaped_default_value)

KEYWORDS = {
    'Escaped Default Value': (escaped_default_value, ['d1=${notvariable}', 'd2=\\\\', 'd3=\n', 'd4=\t']),
    'Four Kw Args': (four_kw_args, ['a=default', 'b=default', 'c=default', 'd=default']),
    'Mandatory, Named And Varargs': (mandatory_named_and_varargs, ['a', 'b=default', '*varargs']),
    'Mandatory And Kwargs': (mandatory_and_kwargs, ['man1', 'man2', 'kwarg=KWARG VALUE']),
    'Mandatory And Named': (mandatory_and_named, ['a', 'b=default']),
    'Named Arguments With Varargs': (named_arguments_with_varargs, ['a=default', 'b=default', '*varargs']),
    'One Kwarg': (one_kwarg, ['kwarg=']),
    'Two Kwargs': (two_kwargs, ['first=', 'second=']),
    u'Nön äscii named args': (two_kwargs, [u'nönäscii=', u'官话='])
}

class DynamicLibrary(object):

    def get_keyword_names(self):
        return KEYWORDS.keys()

    def run_keyword(self, kw_name, args):
        return KEYWORDS[kw_name][0](*args)

    def get_keyword_arguments(self, kw_name):
        return KEYWORDS[kw_name][1]
