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

import os

from writer import FileWriter
from htmltemplate import TEMPLATE


class SerializationContext(object):

    def __init__(self, output=None, format=None, pipe_separated=False,
                 line_separator=os.linesep):
        self._output = output
        self._format = format
        self._pipe_separated = pipe_separated
        self._line_separator = line_separator

    @property
    def pipe_separated(self):
        return self._pipe_separated

    @property
    def line_separator(self):
        return self._line_separator

    def create_template(self, datafile):
        if self.format_for(datafile) in ['html', 'xhtml', 'htm']:
            return TEMPLATE % {'NAME': datafile.name}
        return None

    def get_output(self, datafile):
        return self._output or open(self._get_source(datafile), 'wb')

    def _get_source(self, datafile):
        return getattr(datafile, 'initfile', datafile.source)

    def format_for(self, datafile):
        return self._format or self._format_from_file(datafile)

    def _format_from_file(self, datafile):
        return os.path.splitext(self._get_source(datafile))[1][1:].lower()


class Serializer(object):

    def __init__(self, context=SerializationContext()):
        self._ctx = context

    def serialize(self, datafile):
        template = self._ctx.create_template(datafile)
        output = self._ctx.get_output(datafile)
        self._writer = FileWriter(output,
                                  self._ctx.format_for(datafile),
                                  name=datafile.name,
                                  template=template,
                                  pipe_separated=self._ctx.pipe_separated,
                                  line_separator=self._ctx.line_separator)
        self._serialize(datafile)
        self._close_output()

    def _close_output(self):
        self._writer.close(close_output=self._ctx._output is None)

    def _serialize(self, datafile):
        for table in datafile:
            if table:
                {'setting': self._setting_table_serializer,
                 'variable': self._variable_table_serializer,
                 'keyword': self._keyword_table_serializer,
                 'testcase': self._testcase_table_serializer}[table.type](table)

    def _setting_table_serializer(self, table):
        self._writer.start_settings()
        self._serialize_elements(table)
        self._writer.end_settings()

    def _serialize_elements(self, elements):
        for element in elements:
            if element.is_for_loop():
                self._serialize_for_loop(element)
            elif element.is_set():
                self._writer.element(element)

    def _serialize_for_loop(self, loop):
        self._writer.start_for_loop(loop)
        self._serialize_elements(loop)
        self._writer.end_for_loop()

    def _variable_table_serializer(self, table):
        self._writer.start_variables()
        self._serialize_elements(table)
        self._writer.end_variables()

    def _keyword_table_serializer(self, table):
        self._writer.start_keywords()
        for kw in table:
            self._serialize_keyword(kw)
        self._writer.end_keywords()

    def _serialize_keyword(self, kw):
        self._writer.start_keyword(kw)
        self._serialize_elements(kw)
        self._writer.end_keyword()

    def _testcase_table_serializer(self, table):
        self._writer.start_tests()
        for tc in table:
            self._serialize_testcase(tc)
        self._writer.end_tests()

    def _serialize_testcase(self, tc):
        self._writer.start_testcase(tc)
        self._serialize_elements(tc)
        self._writer.end_testcase()
