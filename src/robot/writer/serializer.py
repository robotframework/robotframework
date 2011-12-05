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

from .writer import FileWriter


class Serializer(object):
    """The Serializer object. It is used to serialize Robot Framework test
    data files.
    """

    def serialize(self, datafile, **options):
        """Serializes given `datafile` using `**options`.

        :param datafile: A robot.parsing.model.DataFile object to be serialized
        :param options: A :py:class:`.SerializationContext` is initialized based on these
        """
        context = SerializationContext(datafile, **options)
        self._writer = FileWriter(context)
        self._serialize(context.datafile)
        self._writer.close()
        return context.finish()

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
        self._writer.start_tests(table)
        for tc in table:
            self._serialize_testcase(tc)
        self._writer.end_tests()

    def _serialize_testcase(self, tc):
        self._writer.start_testcase(tc)
        self._serialize_elements(tc)
        self._writer.end_testcase()


class SerializationContext(object):
    """The SerializationContext object. It holds needed information for
    serializing a test data file.
    """

    def __init__(self, datafile, path=None, format=None, output=None,
                 pipe_separated=False, line_separator=os.linesep):
        """
        :param datafile: The datafile to be serialized.
        :type datafile: :py:class:`~robot.parsing.model.TestCaseFile`,
            :py:class:`~robot.parsing.model.ResourceFile`,
            :py:class:`~robot.parsing.model.TestDataDirectory`
        :param str path: Output file name. If omitted, basename of the `source`
            attribute of the given `datafile` is used. If `path` contains
            extension, it overrides the value of `format` option.
        :param str format: Serialization format. If omitted, read from the
            extension of the `source` attribute of the given `datafile`.
        :param output: An open, file-like object used in serialization. If
            omitted, value of `source` attribute of the given `datafile` is
            used to construct a new file object.
        :param bool pipe_separated: Whether to use pipes as separator when
            serialization format is txt.
        :param str line_separator: Line separator used in serialization.
        """
        self.datafile = datafile
        self.pipe_separated = pipe_separated
        self.line_separator = line_separator
        self._given_output = output
        self._path = path
        self._format = format
        self._output = output

    @property
    def output(self):
        if not self._output:
            self._output = open(self._get_source(), 'wb')
        return self._output

    @property
    def format(self):
        return self._format_from_path() or self._format or self._format_from_file()

    def finish(self):
        if self._given_output is None:
            self._output.close()
        return self._get_source()

    def _get_source(self):
        return self._path or '%s.%s' % (self._basename(), self.format)

    def _basename(self):
        return os.path.splitext(self._source_from_file())[0]

    def _source_from_file(self):
        return getattr(self.datafile, 'initfile', self.datafile.source)

    def _format_from_path(self):
        if not self._path:
            return ''
        return self._format_from_extension(self._path)

    def _format_from_file(self):
        return self._format_from_extension(self._source_from_file())

    def _format_from_extension(self, path):
        return os.path.splitext(path)[1][1:].lower()
