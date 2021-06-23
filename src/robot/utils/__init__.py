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
from .compat import isatty, py2to3, py3to2, StringIO, unwrap, with_metaclass
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
from .misc import (plural_or_not, printable_name, roundup, seq2str,
                   seq2str2, test_or_task)
from .normalizing import lower, normalize, normalize_whitespace, NormalizedDict
from .platform import (IRONPYTHON, JAVA_VERSION, JYTHON, PY_VERSION,
                       PY2, PY3, PYPY, UNIXY, WINDOWS, RERAISED_EXCEPTIONS)
from .recommendations import RecommendationFinder
from .robotenv import get_env_var, set_env_var, del_env_var, get_env_vars
from .robotinspect import is_init, is_java_init, is_java_method
from .robotio import (binary_file_writer, create_destination_directory,
                      file_writer)
from .robotpath import abspath, find_file, get_link_path, normpath
from .robottime import (elapsed_time_to_string, format_time, get_elapsed_time,
                        get_time, get_timestamp, secs_to_timestamp,
                        secs_to_timestr, timestamp_to_secs, timestr_to_secs,
                        parse_time)
from .robottypes import (FALSE_STRINGS, Mapping, MutableMapping, TRUE_STRINGS,
                         is_bytes, is_dict_like, is_falsy, is_integer,
                         is_list_like, is_number, is_pathlike, is_string,
                         is_truthy, is_unicode, type_name, typeddict_types, unicode)
from .setter import setter, SetterAwareType
from .sortable import Sortable
from .text import (cut_assign_value, cut_long_message, format_assign_message,
                   get_console_length, getdoc, getshortdoc, pad_console_length,
                   rstrip, split_tags_from_doc, split_args_from_name_or_path)
from .unic import prepr, unic


def read_rest_data(rstfile):
    from .restreader import read_rest_data
    return read_rest_data(rstfile)
