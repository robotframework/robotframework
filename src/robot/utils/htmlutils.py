#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

import string

from .htmlformatters import LinkFormatter, HtmlFormatter


_html_escapes = (('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'))
_html_attr_escapes = _html_escapes + (('"', '&quot;'),)
_format_url = LinkFormatter().format_url


def html_escape(text):
    return _format_url(_html_escape(text))

def _html_escape(text):
    for name, value in _html_escapes:
        text = text.replace(name, value)
    return text


def html_format(text):
    return HtmlFormatter().format(_html_escape(text))


def html_attr_escape(attr):
    for name, value in _html_attr_escapes:
        attr = attr.replace(name, value)
    for ws in string.whitespace:
        attr = attr.replace(ws, ' ')
    return attr
