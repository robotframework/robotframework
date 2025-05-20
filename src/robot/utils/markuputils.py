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

import re

from .htmlformatters import HtmlFormatter, LinkFormatter

_format_url = LinkFormatter().format_url
_format_html = HtmlFormatter().format
_generic_escapes = (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"))
_attribute_escapes = (
    *_generic_escapes,
    ('"', "&quot;"),
    ("\n", "&#10;"),
    ("\r", "&#13;"),
    ("\t", "&#09;"),
)
_illegal_chars_in_xml = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")


def html_escape(text, linkify=True):
    text = _escape(text)
    if linkify and "://" in text:
        text = _format_url(text)
    return text


def xml_escape(text):
    return _illegal_chars_in_xml.sub("", _escape(text))


def html_format(text):
    return _format_html(_escape(text))


def attribute_escape(attr):
    attr = _escape(attr, _attribute_escapes)
    return _illegal_chars_in_xml.sub("", attr)


def _escape(text, escapes=_generic_escapes):
    for name, value in escapes:
        if name in text:  # performance optimization
            text = text.replace(name, value)
    return text
