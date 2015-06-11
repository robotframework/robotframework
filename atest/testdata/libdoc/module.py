# coding: utf-8

"""Module test library."""

from robot.api import deco


__version__ = '0.1-alpha'


def keyword(a1='d', *a2):
    """A keyword

    See `get hello` for details"""
    pass

def get_hello():
    """Get the intialization variables

    See `importing` for explanation of arguments
    and `introduction` for introduction"""
    return 'foo'

def non_ascii_doc():
    u"""Hyv\u00E4\u00E4 y\u00F6t\u00E4.

    \u0421\u043F\u0430\u0441\u0438\u0431\u043E!"""

def non_ascii_doc_with_bytes():
    """Hyv\xE4\xE4 y\xF6t\xE4."""

def non_ascii_doc_with_declared_utf_8():
    """Hyvää yötä."""

@deco.keyword('Set Name Using Robot Name Attribute')
def name_set_in_method_signature(a, b, *args, **kwargs):
    """
    This makes sure that @deco.keyword decorated kws don't lose their signatures
    """
    pass

@deco.keyword('Takes ${embedded} ${args}')
def takes_embedded_args(a=1, b=2, c=3):
    """A keyword which uses embedded args
    """
    pass

@deco.keyword(tags=['1', 1, 'one', 'yksi'])
def keyword_with_tags_1():
    pass

@deco.keyword('Keyword with tags 2', ('2', 2, 'two', 'kaksi'))
def setting_both_name_and_tags_by_decorator():
    pass
