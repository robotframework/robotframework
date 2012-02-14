# coding: utf-8

"""Module test library."""

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
