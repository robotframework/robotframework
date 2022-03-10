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

"""Various generic utility functions and classes.

Utilities are mainly for internal usage, but external libraries and tools
may find some of them useful. Utilities are generally stable, but absolute
backwards compatibility between major versions is not guaranteed.

All utilities are exposed via the :mod:`robot.utils` package, and should be
used either like::

    from robot import utils

    assert utils.Matcher('H?llo').match('Hillo')

or::

    from robot.utils import Matcher

    assert Matcher('H?llo').match('Hillo')
"""

from .argumentparser import ArgumentParser, cmdline2list
from .application import Application
from .compress import compress_text
from .connectioncache import ConnectionCache
from .dotdict import DotDict
from .encoding import (CONSOLE_ENCODING, SYSTEM_ENCODING, console_decode,
                       console_encode, system_decode, system_encode)
from .error import (get_error_message, get_error_details, ErrorDetails)
from .escaping import escape, glob_escape, unescape, split_from_equals
from .etreewrapper import ET, ETSource
from .filereader import FileReader
from .frange import frange
from .markuputils import html_format, html_escape, xml_escape, attribute_escape
from .markupwriters import HtmlWriter, XmlWriter, NullMarkupWriter
from .importer import Importer
from .match import eq, Matcher, MultiMatcher
from .misc import isatty, plural_or_not, printable_name,seq2str, seq2str2, test_or_task
from .normalizing import normalize, normalize_whitespace, NormalizedDict
from .platform import PY_VERSION, PYPY, UNIXY, WINDOWS, RERAISED_EXCEPTIONS
from .recommendations import RecommendationFinder
from .robotenv import get_env_var, set_env_var, del_env_var, get_env_vars
from .robotinspect import is_init
from .robotio import binary_file_writer, create_destination_directory, file_writer
from .robotpath import abspath, find_file, get_link_path, normpath
from .robottime import (elapsed_time_to_string, format_time, get_elapsed_time,
                        get_time, get_timestamp, secs_to_timestamp,
                        secs_to_timestr, timestamp_to_secs, timestr_to_secs,
                        parse_time)
from .robottypes import (FALSE_STRINGS, TRUE_STRINGS, is_bytes, is_dict_like, is_falsy,
                         is_integer, is_list_like, is_number, is_pathlike, is_string,
                         is_truthy, is_union, type_name, type_repr, typeddict_types)
from .setter import setter, SetterAwareType
from .sortable import Sortable
from .text import (cut_assign_value, cut_long_message, format_assign_message,
                   get_console_length, getdoc, getshortdoc, pad_console_length,
                   split_tags_from_doc, split_args_from_name_or_path)
from .unic import prepr, safe_str


def read_rest_data(rstfile):
    from .restreader import read_rest_data
    return read_rest_data(rstfile)


# Deprecated Python 2/3 compatibility layer. Not needed by Robot Framework itself
# anymore because Python 2 support was dropped in RF 5. Preserved at least until
# RF 5.2 to avoid breaking external libraries and tools that use it. There's also
# `PY2` in the `platform` submodule.
# https://github.com/robotframework/robotframework/issues/4150

from io import StringIO


PY3 = True
PY2 = JYTHON = IRONPYTHON = False
is_unicode = is_string
unicode = str
unic = safe_str
roundup = round


def py2to3(cls):
    """Deprecated since RF 5.0. Use Python 3 features directly instead."""
    if hasattr(cls, '__unicode__'):
        cls.__str__ = lambda self: self.__unicode__()
    if hasattr(cls, '__nonzero__'):
        cls.__bool__ = lambda self: self.__nonzero__()
    return cls


def py3to2(cls):
    """Deprecated since RF 5.0. Never done anything when used on Python 3."""
    return cls
