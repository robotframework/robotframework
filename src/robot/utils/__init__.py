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

from .application import Application as Application
from .argumentparser import (
    ArgumentParser as ArgumentParser,
    cmdline2list as cmdline2list,
)
from .compress import compress_text as compress_text
from .connectioncache import ConnectionCache as ConnectionCache
from .dotdict import DotDict as DotDict
from .encoding import (
    console_decode as console_decode,
    console_encode as console_encode,
    CONSOLE_ENCODING as CONSOLE_ENCODING,
    system_decode as system_decode,
    system_encode as system_encode,
    SYSTEM_ENCODING as SYSTEM_ENCODING,
)
from .error import (
    ErrorDetails as ErrorDetails,
    get_error_details as get_error_details,
    get_error_message as get_error_message,
)
from .escaping import (
    escape as escape,
    glob_escape as glob_escape,
    split_from_equals as split_from_equals,
    unescape as unescape,
)
from .etreewrapper import ETSource as ETSource
from .filereader import FileReader as FileReader, Source as Source
from .frange import frange as frange
from .importer import Importer as Importer
from .json import JsonDumper as JsonDumper, JsonLoader as JsonLoader
from .markuputils import (
    attribute_escape as attribute_escape,
    html_escape as html_escape,
    html_format as html_format,
    xml_escape as xml_escape,
)
from .markupwriters import (
    HtmlWriter as HtmlWriter,
    NullMarkupWriter as NullMarkupWriter,
    XmlWriter as XmlWriter,
)
from .match import eq as eq, Matcher as Matcher, MultiMatcher as MultiMatcher
from .misc import (
    classproperty as classproperty,
    isatty as isatty,
    parse_re_flags as parse_re_flags,
    plural_or_not as plural_or_not,
    printable_name as printable_name,
    seq2str as seq2str,
    seq2str2 as seq2str2,
    test_or_task as test_or_task,
)
from .normalizing import (
    normalize as normalize,
    normalize_whitespace as normalize_whitespace,
    NormalizedDict as NormalizedDict,
)
from .notset import NOT_SET as NOT_SET, NotSet as NotSet
from .platform import (
    PY_VERSION as PY_VERSION,
    PYPY as PYPY,
    UNIXY as UNIXY,
    WINDOWS as WINDOWS,
)
from .recommendations import RecommendationFinder as RecommendationFinder
from .robotenv import (
    del_env_var as del_env_var,
    get_env_var as get_env_var,
    get_env_vars as get_env_vars,
    set_env_var as set_env_var,
)
from .robotinspect import is_init as is_init
from .robotio import (
    binary_file_writer as binary_file_writer,
    create_destination_directory as create_destination_directory,
    file_writer as file_writer,
)
from .robotpath import (
    abspath as abspath,
    find_file as find_file,
    get_link_path as get_link_path,
    normpath as normpath,
)
from .robottime import (
    elapsed_time_to_string as elapsed_time_to_string,
    format_time as format_time,
    get_elapsed_time as get_elapsed_time,
    get_time as get_time,
    get_timestamp as get_timestamp,
    parse_time as parse_time,
    parse_timestamp as parse_timestamp,
    secs_to_timestamp as secs_to_timestamp,
    secs_to_timestr as secs_to_timestr,
    timestamp_to_secs as timestamp_to_secs,
    timestr_to_secs as timestr_to_secs,
)
from .robottypes import (
    has_args as has_args,
    is_dict_like as is_dict_like,
    is_falsy as is_falsy,
    is_list_like as is_list_like,
    is_truthy as is_truthy,
    is_union as is_union,
    type_name as type_name,
    type_repr as type_repr,
    typeddict_types as typeddict_types,
)
from .setter import setter as setter, SetterAwareType as SetterAwareType
from .sortable import Sortable as Sortable
from .text import (
    cut_assign_value as cut_assign_value,
    cut_long_message as cut_long_message,
    format_assign_message as format_assign_message,
    get_console_length as get_console_length,
    getdoc as getdoc,
    getshortdoc as getshortdoc,
    pad_console_length as pad_console_length,
    split_args_from_name_or_path as split_args_from_name_or_path,
    split_tags_from_doc as split_tags_from_doc,
)
from .typehints import (
    copy_signature as copy_signature,
    KnownAtRuntime as KnownAtRuntime,
)
from .unic import prepr as prepr, safe_str as safe_str


def read_rest_data(rstfile):
    from .restreader import read_rest_data

    return read_rest_data(rstfile)


def unic(item):
    # Cannot be deprecated using '__getattr__' because a module with same name exists.
    warnings.warn(
        "'robot.utils.unic' is deprecated and will be removed in Robot Framework 9.0.",
        DeprecationWarning,
    )
    return safe_str(item)


def __getattr__(name):
    # Deprecated utils mostly related to the old Python 2/3 compatibility layer.
    # See also 'unic' above and 'PY2' in 'platform.py'.
    # https://github.com/robotframework/robotframework/issues/4501

    from io import StringIO
    from os import PathLike
    from xml.etree import ElementTree as ET

    from .robottypes import FALSE_STRINGS, TRUE_STRINGS

    def py2to3(cls):
        if hasattr(cls, "__unicode__"):
            cls.__str__ = lambda self: self.__unicode__()
        if hasattr(cls, "__nonzero__"):
            cls.__bool__ = lambda self: self.__nonzero__()
        return cls

    def py3to2(cls):
        return cls

    def is_integer(item):
        return isinstance(item, int)

    def is_number(item):
        return isinstance(item, (int, float))

    def is_bytes(item):
        return isinstance(item, (bytes, bytearray))

    def is_string(item):
        return isinstance(item, str)

    def is_pathlike(item):
        return isinstance(item, PathLike)

    deprecated = {
        "RERAISED_EXCEPTIONS": (KeyboardInterrupt, SystemExit, MemoryError),
        "FALSE_STRINGS": FALSE_STRINGS,
        "TRUE_STRINGS": TRUE_STRINGS,
        "ET": ET,
        "StringIO": StringIO,
        "PY3": True,
        "PY2": False,
        "JYTHON": False,
        "IRONPYTHON": False,
        "is_number": is_number,
        "is_integer": is_integer,
        "is_pathlike": is_pathlike,
        "is_bytes": is_bytes,
        "is_string": is_string,
        "is_unicode": is_string,
        "unicode": str,
        "roundup": round,
        "py2to3": py2to3,
        "py3to2": py3to2,
    }

    if name in deprecated:
        # TODO: Change DeprecationWarning to more visible UserWarning in RF 8.0.
        # https://github.com/robotframework/robotframework/issues/4501
        # Remember also 'unic' above '__getattr__' and 'PY2' in 'platform.py'.
        warnings.warn(
            f"'robot.utils.{name}' is deprecated and will be removed in "
            f"Robot Framework 9.0.",
            DeprecationWarning,
        )
        return deprecated[name]

    raise AttributeError(f"'robot.utils' has no attribute '{name}'.")
