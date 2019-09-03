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

from robot.errors import DataError
from robot.utils import file_writer

from .filewriters import write_to_file


class DataFileWriter(object):
    """Object to write parsed test data file objects back to disk."""

    def __init__(self, **options):
        """
        :param `**options`: A :class:`.WritingContext` is created based on these.
        """
        self._options = options

    def write(self, model):
        # TODO: Fix the documentation and types
        """Writes given `model` to output using `**options`.

        :param model: The parsed test data object to be written
        :type model: :py:class:`~robot.parsing.model.TestCaseFile`,
            :py:class:`~robot.parsing.model.ResourceFile`,
            :py:class:`~robot.parsing.model.TestDataDirectory`
        """

        with WritingContext(model, **self._options) as ctx:
            write_to_file(ctx, model)


class WritingContext(object):
    """Contains configuration used in writing a test data file to disk."""
    txt_format = 'txt'
    robot_format = 'robot'
    _formats = [txt_format, robot_format]

    def __init__(self, datafile, format='', output=None, pipe_separated=False,
                 path=None, txt_separating_spaces=4, line_separator='\n'):
        """
        :param datafile: The datafile to be written.
        :type datafile: :py:class:`~robot.parsing.model.TestCaseFile`,
            :py:class:`~robot.parsing.model.ResourceFile`,
            :py:class:`~robot.parsing.model.TestDataDirectory`
        :param str format: Output file format. If omitted, read from the
            extension of the `source` attribute of the given `datafile`.
        :param output: An open, file-like object used in writing. If
            omitted, value of `source` attribute of the given `datafile` is
            used to construct a new file object.
        :param bool pipe_separated: Whether to use pipes as separator when
            output file format is txt.
        :param int txt_separating_spaces: Number of separating spaces between
            cells in space separated format.
        :param str line_separator: Line separator used in output files.

        If `output` is not given, an output file is created based on the source
        of the given datafile and value of `format`. Examples:

        Write output in a StringIO instance using format of `datafile.source`::

            WriteConfiguration(datafile, output=StringIO)

        Output file is created from `datafile.source` by stripping extension
        and replacing it with `html`::

            WriteConfiguration(datafile, format='html')
        """
        self.datafile = datafile
        self.pipe_separated = pipe_separated
        self.line_separator = line_separator
        self._given_output = output
        self.format = self._validate_format(format)
        self.txt_separating_spaces = txt_separating_spaces
        self.setting_and_variable_name_length = 14
        self.short_test_name_length = 18
        self.output = output
        self._path = path

    def __enter__(self):
        if not self.output:
            self.output = file_writer(self._path, newline=self.line_separator)
        return self

    def __exit__(self, *exc_info):
        if self._given_output is None:
            self.output.close()

    def _validate_format(self, format):
        format = format.lower() if format else ''
        if format and format not in self._formats:
            raise DataError('Invalid format: %s' % format)
        return format
