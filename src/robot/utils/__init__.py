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

from .application import Application
from .argumentparser import ArgumentParser, cmdline2list
from .compat import StringIO, isatty, py2to3, with_metaclass
from .compress import compress_text
from .connectioncache import ConnectionCache
from .dotdict import DotDict
from .encoding import (CONSOLE_ENCODING, SYSTEM_ENCODING, console_decode,
                       console_encode, system_decode, system_encode)
from .error import ErrorDetails, get_error_details, get_error_message
from .escaping import escape, split_from_equals, unescape
from .etreewrapper import ET, ETSource
from .filereader import FileReader
from .frange import frange
from .importer import Importer
from .markuputils import attribute_escape, html_escape, html_format, xml_escape
from .markupwriters import HtmlWriter, NullMarkupWriter, XmlWriter
from .match import Matcher, MultiMatcher, eq
from .misc import plural_or_not, printable_name, roundup, seq2str, seq2str2
from .normalizing import NormalizedDict, lower, normalize, normalize_whitespace
from .platform import (IRONPYTHON, JAVA_VERSION, JYTHON, PY2, PY3, PY_VERSION,
                       PYPY, RERAISED_EXCEPTIONS, UNIXY, WINDOWS)
from .recommendations import RecommendationFinder
from .robotenv import del_env_var, get_env_var, get_env_vars, set_env_var
from .robotinspect import is_java_init, is_java_method
from .robotio import (binary_file_writer, create_destination_directory,
                      file_writer)
from .robotpath import abspath, find_file, get_link_path, normpath
from .robottime import (elapsed_time_to_string, format_time, get_elapsed_time,
                        get_time, get_timestamp, parse_time, secs_to_timestamp,
                        secs_to_timestr, timestamp_to_secs, timestr_to_secs)
from .robottypes import (FALSE_STRINGS, TRUE_STRINGS, Mapping, MutableMapping,
                         is_bytes, is_dict_like, is_falsy, is_integer,
                         is_list_like, is_number, is_sequence, is_string,
                         is_subscriptable, is_truthy, is_unicode, type_name,
                         unicode)
from .setter import SetterAwareType, setter
from .sortable import Sortable
from .text import (cut_long_message, format_assign_message, get_console_length,
                   getdoc, getshortdoc, pad_console_length, rstrip,
                   split_args_from_name_or_path, split_tags_from_doc)
from .unic import prepr, unic


def read_rest_data(rstfile):
    from .restreader import read_rest_data
    return read_rest_data(rstfile)
