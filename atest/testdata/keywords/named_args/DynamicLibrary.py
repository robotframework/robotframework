#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dynamic_library_impl import var_args, return_argument, return_arguments

KEYWORDS = {
    'Escaped Default Value': (var_args, ['d1=${notvariable}', 'd2=\\\\', 'd3=\n', 'd4=\t']),
    'Four Kw Args': (var_args, ['a=default', 'b=default', 'c=default', 'd=default']),
    'Mandatory, Named And Varargs': (var_args, ['a', 'b=default', '*varargs']),
    'Mandatory And Kwargs': (var_args, ['man1', 'man2', 'kwarg=KWARG VALUE']),
    'Mandatory And Named': (var_args, ['a', 'b=default']),
    'Named Arguments With Varargs': (return_arguments, ['a=default', 'b=default', '*varargs']),
    'One Kwarg Returned': (return_argument, ['kwarg=']),
    'Two Kwargs': (var_args, ['first=', 'second=']),
    u'Nön äscii named args': (var_args, [u'nönäscii=', u'官话=']),
    'three named': (var_args, ['a=a', 'b=b', 'c=c'])
}

class DynamicLibrary(object):

    def get_keyword_names(self):
        return KEYWORDS.keys()

    def run_keyword(self, kw_name, args):
        return KEYWORDS[kw_name][0](*args)

    def get_keyword_arguments(self, kw_name):
        return KEYWORDS[kw_name][1]
