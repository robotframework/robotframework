#  Copyright 2008-2014 Nokia Solutions and Networks
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
from .encoding import (decode_output, encode_output,
                       decode_from_system, encode_to_system)
from .error import (get_error_message, get_error_details, ErrorDetails,
                    RERAISED_EXCEPTIONS)
from .escaping import escape, unescape
from .etreewrapper import ET, ETSource
from .frange import frange
from .markuputils import html_format, html_escape, xml_escape, attribute_escape
from .markupwriters import HtmlWriter, XmlWriter, NullMarkupWriter
from .importer import Importer
from .islike import is_dict_like, is_list_like, is_str_like
from .match import eq, Matcher, MultiMatcher
from .misc import (isatty, getdoc, plural_or_not, printable_name,
                   seq2str, seq2str2)
from .normalizing import lower, normalize, NormalizedDict
from .recommendations import RecommendationFinder
from .robotenv import get_env_var, set_env_var, del_env_var, get_env_vars
from .robotinspect import is_java_init, is_java_method
from .robotpath import abspath, find_file, get_link_path, normpath
from .robottime import (get_timestamp, get_start_timestamp, format_time,
                        get_time, get_elapsed_time, elapsed_time_to_string,
                        timestr_to_secs, secs_to_timestr, secs_to_timestamp,
                        timestamp_to_secs, parse_time)
from .setter import setter
from .text import (cut_long_message, format_assign_message,
                   pad_console_length, get_console_length)
from .unic import unic, safe_repr
from .utf8reader import Utf8Reader

import sys
is_jython = sys.platform.startswith('java')
del sys


# Following utils were removed in 2.8 but added back in 2.8.1 because they
# were used by SSHLibrary and SeleniumLibrary. Libs must be changed not to
# use them and then, hopefully, we can remove them again in 2.9.
# https://code.google.com/p/robotframework/issues/detail?id=1472

def matches(string, pattern, ignore=(), caseless=True, spaceless=True):
    """Deprecated!! Use Matcher instead."""
    return Matcher(pattern, ignore, caseless, spaceless).match(string)

def html_attr_escape(attr):
    """Deprecated!! Use attribute_escape instead."""
    return attribute_escape(attr)
