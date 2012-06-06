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

import os
import re

from .htmlwriter import MarkupWriter
from .markuputils import xml_escape, attribute_escape
from .unic import unic


class XmlWriter(MarkupWriter):
    _illegal_chars = re.compile(u'[\x00-\x08\x0B\x0C\x0E-\x1F\uFFFE\uFFFF]')

    def __init__(self, output, line_separator=os.linesep, encoding=None):
        MarkupWriter.__init__(self, self._create_output(output),
                              line_separator, encoding)
        self._preamble()

    def _create_output(self, output):
        return open(output, 'w') \
            if isinstance(output, basestring) else output

    def _preamble(self):
        self.content('<?xml version="1.0" encoding="UTF-8"?>\n', escape=False)

    def _escape(self, text):
        text = xml_escape(text)
        return self._illegal_chars.sub('', unic(text))

    def _format_attributes(self, attrs):
        return ('%s="%s"' % (name, attribute_escape(unicode(attrs[name])))
                             for name in attrs)
