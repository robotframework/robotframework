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

import re
from StringIO import StringIO
try:
    import csv
except ImportError:
    # csv module is missing from IronPython < 2.7.1
    csv = None

from robot import utils

from .formatters import TsvFormatter, TxtFormatter, PipeFormatter, HtmlFormatter
from .htmltemplate import TEMPLATE_START, TEMPLATE_END


def FileWriter(serialization_context):
    """Creates and returns a FileWriter object.

    :param serialization_context: Type of returned
        FileWriter is determined based on `serialization_context.format`.
        Is also passed along to created writer for further configuration.
    :type serialization_context: :py:class:`SerializationContext`
    """
    Writer = {
        'tsv': TsvFileWriter,
        'txt': TxtFileWriter,
        'html': HtmlFileWriter
    }[serialization_context.format]
    return Writer(serialization_context)


def TxtFileWriter(context):
    Writer = PipeSeparatedTxtWriter if context.pipe_separated else SpaceSeparatedTxtWriter
    return Writer(context)


class _DataFileWriter(object):

    def write(self, datafile):
        for table in datafile:
            if table:
                self._write_header(table)
                self._write_rows(self._formatted_table(table))
                self._write_empty_row()

    def _formatted_table(self, table):
        formatter = {'setting': self._formatter.setting_rows,
                     'variable': self._formatter.variable_rows,
                     'testcase': self._formatter.test_rows,
                     'keyword': self._formatter.keyword_rows
                    }[table.type]
        return formatter(table)

    def _write_header(self, table):
        self._write_row(self._formatter.header_row(table))

    def _write_empty_row(self):
        self._write_row(self._formatter.empty_row())


class _TextFileWriter(_DataFileWriter):

    def __init__(self, context, formatter):
        self._output = context.output
        self._line_separator = context.line_separator
        self._formatter = formatter

    def _write_rows(self, rows):
        for row in rows:
            self._write_row(row)


class SpaceSeparatedTxtWriter(_TextFileWriter):
    _separator = ' '*4

    def __init__(self, context):
        _TextFileWriter.__init__(self, context, TxtFormatter())

    def _write_row(self, row):
        self._output.write(self._separator.join(row) + self._line_separator)


class PipeSeparatedTxtWriter(_TextFileWriter):
    _separator = ' | '

    def __init__(self, context):
        _TextFileWriter.__init__(self, context, PipeFormatter())

    def _write_row(self, row):
        row = self._separator.join(row)
        if row:
            row = '| ' + row + ' |'
        self._output.write(row + self._line_separator)


class TsvFileWriter(_TextFileWriter):

    def __init__(self, context):
        if not csv:
            raise RuntimeError('No csv module found. '
                               'Writing tab separated format is not possible.')
        _TextFileWriter.__init__(self, context, TsvFormatter())
        self._writer = csv.writer(context.output, dialect='excel-tab',
                                  lineterminator=context.line_separator)

    def _write_row(self, row):
        self._writer.writerow(row)


class HtmlFileWriter(_DataFileWriter):

    def __init__(self, context):
        self._name = context.datafile.name
        self._writer = utils.HtmlWriter(context.output)
        self._formatter = HtmlFormatter()

    def write(self, datafile):
        self._writer.content(TEMPLATE_START % {'NAME': self._name}, escape=False)
        for table in datafile:
            if table:
                self._writer.start('table', {'id': table.type, 'border': '1'})
                self._write_header(table)
                {'setting': self._write_settings,
                 'variable': self._write_variables,
                 'testcase': self._write_tests,
                 'keyword': self._write_keywords
                 }[table.type](table)
                self._write_empty_row()
                self._writer.end('table')
        self._writer.content(TEMPLATE_END, escape=False)

    def _write_settings(self, settings):
        self._write_table(self._formatter.setting_rows(settings))

    def _write_variables(self, variables):
        self._write_table(self._formatter.variable_rows(variables))

    def _write_tests(self, tests):
        self._write_table(self._formatter.test_rows(tests))

    def _write_keywords(self, keywords):
        self._write_table(self._formatter.keyword_rows(keywords))

    def _write_table(self, rows):
        for row in rows:
            self._write_row(row)

    def _end_table(self, table_replacer):
        self._write_empty_row()
        table = self._writer.output.getvalue().decode('UTF-8')
        self._content = table_replacer(table, self._content)
        self._writer = utils.HtmlWriter(StringIO())

    def _write_row(self, row):
        self._writer.start('tr')
        for cell in row:
            self._writer.element(cell.tag, cell.content, cell.attributes,
                                 escape=False)
        self._writer.end('tr')
