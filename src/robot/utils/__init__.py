#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

from argumentparser import ArgumentParser
from connectioncache import ConnectionCache
from domwrapper import DomWrapper
from encoding import decode_output, encode_output
from error import (get_error_message, get_error_details, ErrorDetails,
                   RERAISED_EXCEPTIONS)
from escaping import escape, unescape
from htmlutils import html_escape, html_attr_escape
from htmlwriter import HtmlWriter
from idgenerator import IdGenerator, FileNameGenerator
from importing import simple_import, import_
from match import eq, eq_any, matches, matches_any
from misc import plural_or_not, get_link_path, printable_name, seq2str, seq2str2
from normalizing import normalize, normalize_tags, normpath, NormalizedDict
from robottime import (get_timestamp, get_start_timestamp, format_time,
                       get_time, get_elapsed_time, elapsed_time_to_string,
                       timestr_to_secs, secs_to_timestr, secs_to_timestamp,
                       timestamp_to_secs, parse_time)
from text import (cut_long_message, format_assign_message,
                  pad_console_length, get_console_length)
from unic import unic, safe_repr
from xmlwriter import XmlWriter

import sys
is_jython  = sys.platform.startswith('java')
del sys
