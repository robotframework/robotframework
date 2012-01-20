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
from robot.writer.htmlformatter import HtmlFormatter

try:
    import csv
except ImportError:
    # csv module is missing from IronPython < 2.7.1
    csv = None

from robot import utils

from .formatters import TsvFormatter, TxtFormatter, PipeFormatter
from .htmltemplate import TEMPLATE_START, TEMPLATE_END


def FileWriter(configuration):
    """Creates and returns a FileWriter object.

    :param configuration: Type of returned FileWriter is determined based on
        `configuration.format`. `configuration` is also passed to created
        writer.
    :type configuration: :py:class:`WriteConfiguration`
    """
    writer_class = {'tsv': TsvFileWriter,
                    'txt': TxtFileWriter,
                    'html': HtmlFileWriter}[configuration.format]
    return writer_class(configuration)


def TxtFileWriter(configuration):
    writer_class = PipeSeparatedTxtWriter if configuration.pipe_separated \
            else SpaceSeparatedTxtWriter
    return writer_class(configuration)


class _DataFileWriter(object):
    _formatter = None

    def __init__(self, configuration):
        self._output = configuration.output
        self._line_separator = configuration.line_separator

    def write(self, datafile):
        for table in datafile:
            if table:
                self._write_table(table)

    def _write_table(self, table):
        self._write_header(table)
        self._write_rows(self._formatted_table(table))
        self._write_empty_row()

    def _write_header(self, table):
        self._write_row(self._formatter.header_row(table))

    def _formatted_table(self, table):
        formatter = {'setting': self._formatter.setting_table,
                     'variable': self._formatter.variable_table,
                     'test case': self._formatter.test_table,
                     'keyword': self._formatter.keyword_table}[table.type]
        return formatter(table)

    def _write_empty_row(self):
        self._write_row(self._formatter.empty_row())

    def _write_rows(self, rows):
        for row in rows:
            self._write_row(row)

    def _encode(self, row):
        return row.encode('UTF-8')


class SpaceSeparatedTxtWriter(_DataFileWriter):
    _separator = ' '*4
    _formatter = TxtFormatter(cols=8)

    def _write_row(self, row):
        line = self._separator.join(row) + self._line_separator
        self._output.write(self._encode(line))


class PipeSeparatedTxtWriter(_DataFileWriter):
    _separator = ' | '
    _formatter = PipeFormatter(cols=8)

    def _write_row(self, row):
        row = self._separator.join(row)
        if row:
            row = '| ' + row + ' |'
        self._output.write(self._encode(row + self._line_separator))


class TsvFileWriter(_DataFileWriter):
    _formatter = TsvFormatter(cols=8)

    def __init__(self, configuration):
        if not csv:
            raise RuntimeError('No csv module found. '
                               'Writing tab separated format is not possible.')
        _DataFileWriter.__init__(self, configuration)
        self._writer = csv.writer(configuration.output, dialect='excel-tab',
                                  lineterminator=configuration.line_separator)

    def _write_row(self, row):
        self._writer.writerow(self._encode(row))

    def _encode(self, row):
        return [c.encode('UTF-8') for c in row]


class HtmlFileWriter(_DataFileWriter):
    _formatter = HtmlFormatter(cols=5)

    def __init__(self, configuration):
        _DataFileWriter.__init__(self, configuration)
        self._name = configuration.datafile.name
        self._writer = utils.HtmlWriter(configuration.output,
                                        configuration.line_separator,
                                        encoding='UTF-8')

    def write(self, datafile):
        self._writer.content(TEMPLATE_START % {'NAME': self._name},
                             escape=False)
        _DataFileWriter.write(self, datafile)
        self._writer.content(TEMPLATE_END, escape=False)

    def _write_table(self, table):
        self._writer.start('table', {'id': table.type.replace(' ', ''),
                                     'border': '1'})
        _DataFileWriter._write_table(self, table)
        self._writer.end('table')

    def _write_row(self, row):
        self._writer.start('tr')
        for cell in row:
            self._writer.element(cell.tag, cell.content, cell.attributes,
                                 escape=False)
        self._writer.end('tr')
