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

import warnings

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
from .filereader import FileReader, Source
from .frange import frange
from .markuputils import html_format, html_escape, xml_escape, attribute_escape
from .markupwriters import HtmlWriter, XmlWriter, NullMarkupWriter
from .importer import Importer
from .json import JsonDumper, JsonLoader
from .match import eq, Matcher, MultiMatcher
from .misc import (classproperty, isatty, parse_re_flags, plural_or_not,
                   printable_name, seq2str, seq2str2, test_or_task)
from .normalizing import normalize, normalize_whitespace, NormalizedDict
from .notset import NOT_SET, NotSet
from .platform import PY_VERSION, PYPY, UNIXY, WINDOWS, RERAISED_EXCEPTIONS
from .recommendations import RecommendationFinder
from .robotenv import get_env_var, set_env_var, del_env_var, get_env_vars
from .robotinspect import is_init
from .robotio import binary_file_writer, create_destination_directory, file_writer
from .robotpath import abspath, find_file, get_link_path, normpath
from .robottime import (elapsed_time_to_string, format_time, get_elapsed_time,
                        get_time, get_timestamp, secs_to_timestamp,
                        secs_to_timestr, timestamp_to_secs, timestr_to_secs,
                        parse_time, parse_timestamp)
from .robottypes import (has_args, is_bytes, is_dict_like, is_falsy, is_integer,
                         is_list_like, is_number, is_pathlike, is_string, is_truthy,
                         is_union, type_name, type_repr, typeddict_types)
from .setter import setter, SetterAwareType
from .sortable import Sortable
from .text import (cut_assign_value, cut_long_message, format_assign_message,
                   get_console_length, getdoc, getshortdoc, pad_console_length,
                   split_tags_from_doc, split_args_from_name_or_path)
from .typehints import copy_signature, KnownAtRuntime
from .unic import prepr, safe_str


def read_rest_data(rstfile):
    from .restreader import read_rest_data
    return read_rest_data(rstfile)


def unic(item):
    # Cannot be deprecated using '__getattr__' because a module with same name exists.
    warnings.warn("'robot.utils.unic' is deprecated and will be removed in "
                  "Robot Framework 9.0.", DeprecationWarning)
    return safe_str(item)


def __getattr__(name):
    # Deprecated utils mostly related to the old Python 2/3 compatibility layer.
    # See also 'unic' above and 'PY2' in 'platform.py'.
    # https://github.com/robotframework/robotframework/issues/4501

    from io import StringIO
    from .robottypes import FALSE_STRINGS, TRUE_STRINGS

    def py2to3(cls):
        if hasattr(cls, '__unicode__'):
            cls.__str__ = lambda self: self.__unicode__()
        if hasattr(cls, '__nonzero__'):
            cls.__bool__ = lambda self: self.__nonzero__()
        return cls

    def py3to2(cls):
        return cls

    deprecated = {
        'FALSE_STRINGS': FALSE_STRINGS,
        'TRUE_STRINGS': TRUE_STRINGS,
        'StringIO': StringIO,
        'PY3': True,
        'PY2': False,
        'JYTHON': False,
        'IRONPYTHON': False,
        'is_unicode': is_string,
        'unicode': str,
        'roundup': round,
        'py2to3': py2to3,
        'py3to2': py3to2,
    }

    if name in deprecated:
        # TODO: Change DeprecationWarning to more visible UserWarning in RF 8.0.
        # https://github.com/robotframework/robotframework/issues/4501
        # Remember also 'unic' above '__getattr__' and 'PY2' in 'platform.py'.
        warnings.warn(f"'robot.utils.{name}' is deprecated and will be removed in "
                      f"Robot Framework 9.0.", DeprecationWarning)
        return deprecated[name]

    raise AttributeError(f"'robot.utils' has no attribute '{name}'.")
