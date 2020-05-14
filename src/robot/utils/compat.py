#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys

from .platform import IRONPYTHON, PY2


if PY2:
    # io.StringIO only accepts u'foo' with Python 2.
    from StringIO import StringIO


    def py2to3(cls):
        if hasattr(cls, '__unicode__'):
            cls.__str__ = lambda self: unicode(self).encode('UTF-8')
        return cls


    def unwrap(func):
        return func

else:
    from inspect import unwrap
    from io import StringIO


    def py2to3(cls):
        if hasattr(cls, '__unicode__'):
            cls.__str__ = lambda self: self.__unicode__()
        if hasattr(cls, '__nonzero__'):
            cls.__bool__ = lambda self: self.__nonzero__()
        return cls


# Copied from Jinja2, released under the BSD license.
# https://github.com/mitsuhiko/jinja2/blob/743598d788528921df825479d64f492ef60bef82/jinja2/_compat.py#L88
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.
    class metaclass(type):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


# On IronPython sys.stdxxx.isatty() always returns True
if not IRONPYTHON:

    def isatty(stream):
        # first check if buffer was detached
        if hasattr(stream, 'buffer') and stream.buffer is None:
            return False
        if not hasattr(stream, 'isatty'):
            return False
        try:
            return stream.isatty()
        except ValueError:    # Occurs if file is closed.
            return False

else:

    from ctypes import windll

    _HANDLE_IDS = {sys.__stdout__ : -11, sys.__stderr__ : -12}
    _CONSOLE_TYPE = 2

    def isatty(stream):
        if stream not in _HANDLE_IDS:
            return False
        handle = windll.kernel32.GetStdHandle(_HANDLE_IDS[stream])
        return windll.kernel32.GetFileType(handle) == _CONSOLE_TYPE
