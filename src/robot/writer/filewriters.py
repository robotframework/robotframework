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

try:
    import csv
except ImportError:
    # csv module is missing from IronPython < 2.7.1
    csv = None

from robot import utils

from .formatters import TsvFormatter, TxtFormatter, PipeFormatter
from .htmlformatter import HtmlFormatter
from .htmltemplate import TEMPLATE_START, TEMPLATE_END


def FileWriter(context):
    """Creates and returns a FileWriter object.

    :param context: Type of returned FileWriter is determined based on
        `context.format`. `context` is also passed to created writer.
    :type context: :py:class:`WritingContext`
    """
    if context.format == context.html_format:
        return HtmlFileWriter(context)
    if context.format == context.tsv_format:
        return TsvFileWriter(context)
    if context.pipe_separated:
        return PipeSeparatedTxtWriter(context)
    return SpaceSeparatedTxtWriter(context)


class _DataFileWriter(object):

    def __init__(self, formatter, configuration):
        self._formatter = formatter
        self._output = configuration.output
        self._line_separator = configuration.line_separator
        self._encoding = configuration.encoding

    def write(self, datafile):
        tables = [table for table in datafile if table]
        for table in tables:
            self._write_table(table, is_last=table is tables[-1])

    def _write_table(self, table, is_last):
        self._write_header(table)
        self._write_rows(self._formatter.format_table(table))
        if not is_last:
            self._write_empty_row(table)

    def _write_header(self, table):
        self._write_row(self._formatter.format_header(table))

    def _write_rows(self, rows):
        for row in rows:
            self._write_row(row)

    def _write_empty_row(self, table):
        self._write_row(self._formatter.empty_row_after(table))

    def _encode(self, row):
        return row.encode(self._encoding)

    def _write_row(self, row):
        raise NotImplementedError


class SpaceSeparatedTxtWriter(_DataFileWriter):

    def __init__(self, configuration):
        formatter = TxtFormatter(configuration.txt_column_count)
        self._separator = ' ' * configuration.txt_separating_spaces
        _DataFileWriter.__init__(self, formatter, configuration)

    def _write_row(self, row):
        line = self._separator.join(row).rstrip() + self._line_separator
        self._output.write(self._encode(line))


class PipeSeparatedTxtWriter(_DataFileWriter):
    _separator = ' | '

    def __init__(self, configuration):
        formatter = PipeFormatter(configuration.txt_column_count)
        _DataFileWriter.__init__(self, formatter, configuration)

    def _write_row(self, row):
        row = self._separator.join(row)
        if row:
            row = '| ' + row + ' |'
        self._output.write(self._encode(row + self._line_separator))


class TsvFileWriter(_DataFileWriter):

    def __init__(self, configuration):
        if not csv:
            raise RuntimeError('No csv module found. '
                               'Writing tab separated format is not possible.')
        formatter = TsvFormatter(configuration.tsv_column_count)
        _DataFileWriter.__init__(self, formatter, configuration)
        self._writer = self._get_writer(configuration)

    def _get_writer(self, configuration):
        # Custom dialect needed as a workaround for
        # http://ironpython.codeplex.com/workitem/33627
        dialect = csv.excel_tab()
        dialect.lineterminator = configuration.line_separator
        return csv.writer(configuration.output, dialect=dialect)

    def _write_row(self, row):
        self._writer.writerow([self._encode(c) for c in row])


class HtmlFileWriter(_DataFileWriter):

    def __init__(self, configuration):
        formatter = HtmlFormatter(configuration.html_column_count)
        _DataFileWriter.__init__(self, formatter, configuration)
        self._name = configuration.datafile.name
        self._writer = utils.HtmlWriter(configuration.output,
                                        configuration.line_separator,
                                        encoding=self._encoding)

    def write(self, datafile):
        self._writer.content(TEMPLATE_START % {'NAME': self._name},
                             escape=False, replace_newlines=True)
        _DataFileWriter.write(self, datafile)
        self._writer.content(TEMPLATE_END, escape=False, replace_newlines=True)

    def _write_table(self, table, is_last):
        self._writer.start('table', {'id': table.type.replace(' ', ''),
                                     'border': '1'})
        _DataFileWriter._write_table(self, table, is_last)
        self._writer.end('table')

    def _write_row(self, row):
        self._writer.start('tr')
        for cell in row:
            self._writer.element(cell.tag, cell.content, cell.attributes,
                                 escape=False)
        self._writer.end('tr')
