#  Copyright 2008-2015 Nokia Solutions and Networks
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

from .argumentparser import ArgumentParser
from .application import Application
from .compress import compress_text
from .connectioncache import ConnectionCache
from .dotdict import DotDict, OrderedDict
from .encoding import (decode_output, encode_output,
                       decode_from_system, encode_to_system)
from .error import (get_error_message, get_error_details, ErrorDetails,
                    RERAISED_EXCEPTIONS)
from .escaping import escape, unescape, split_from_equals
from .etreewrapper import ET, ETSource
from .frange import frange
from .markuputils import html_format, html_escape, xml_escape, attribute_escape
from .markupwriters import HtmlWriter, XmlWriter, NullMarkupWriter
from .importer import Importer
from .match import eq, Matcher, MultiMatcher
from .misc import (isatty, getdoc, plural_or_not, printable_name,
                   seq2str, seq2str2)
from .normalizing import lower, normalize, NormalizedDict
from .platform import IRONPYTHON, JYTHON, PYTHON, UNIXY, WINDOWS
from .recommendations import RecommendationFinder
from .robotenv import get_env_var, set_env_var, del_env_var, get_env_vars
from .robotinspect import is_java_init, is_java_method
from .robotpath import abspath, find_file, get_link_path, normpath
from .robottime import (elapsed_time_to_string, format_time, get_elapsed_time,
                        get_time, get_timestamp, secs_to_timestamp,
                        secs_to_timestr, timestamp_to_secs, timestr_to_secs,
                        parse_time)
from .robottypes import (is_dict_like, is_falsy, is_list_like, is_str_like,
                         is_truthy, type_name)
from .setter import setter
from .text import (cut_long_message, format_assign_message,
                   pad_console_length, get_console_length, split_tags_from_doc,
                   split_args_from_name_or_path)
from .unic import prepr, unic
from .utf8reader import Utf8Reader


# Still used by old SeleniumLibrary. Cannot be removed until that library is
# updated or officially retired.
# https://code.google.com/p/robotframework-seleniumlibrary/issues/detail?id=261
def html_attr_escape(attr):
    """Deprecated!! Use attribute_escape instead."""
    return attribute_escape(attr)
