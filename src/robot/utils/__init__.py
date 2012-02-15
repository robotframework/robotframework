#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
from .htmlutils import html_format, html_escape, html_attr_escape
from .htmlwriter import HtmlWriter
from .importer import Importer
from .match import eq, matches, matches_any, Matcher
from .misc import plural_or_not, printable_name, seq2str, seq2str2, getdoc
from .normalizing import normalize, normalize_tags, NormalizedDict
from .robotenv import get_env_var, set_env_var, del_env_var
from .robotpath import normpath, abspath, get_link_path
from .robottime import (get_timestamp, get_start_timestamp, format_time,
                        get_time, get_elapsed_time, elapsed_time_to_string,
                        timestr_to_secs, secs_to_timestr, secs_to_timestamp,
                        timestamp_to_secs, parse_time)
from .setter import setter
from .text import (cut_long_message, format_assign_message,
                  pad_console_length, get_console_length)
from .unic import unic, safe_repr
from .xmlwriter import XmlWriter

import sys
is_jython = sys.platform.startswith('java')
del sys
