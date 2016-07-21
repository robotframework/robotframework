#!/usr/bin/env python

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

"""Module implementing the command line entry point for the `Tidy` tool.

This module can be executed from the command line using the following
approaches::

    python -m robot.tidy
    python path/to/robot/tidy.py

Instead of ``python`` it is possible to use also other Python interpreters.

This module also provides :class:`Tidy` class and :func:`tidy_cli` function
that can be used programmatically. Other code is for internal usage.
"""

import os
import sys

# Allows running as a script. __name__ check needed with multiprocessing:
# https://github.com/robotframework/robotframework/issues/1137
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter

from robot.errors import DataError
from robot.parsing import (ResourceFile, TestDataDirectory, TestCaseFile,
                           disable_curdir_processing)
from robot.utils import Application, binary_file_writer, file_writer, PY2


USAGE = """robot.tidy -- Robot Framework test data clean-up tool

Version:  <VERSION>

Usage:  python -m robot.tidy [options] inputfile
   or:  python -m robot.tidy [options] inputfile [outputfile]
   or:  python -m robot.tidy --inplace [options] inputfile [more input files]
   or:  python -m robot.tidy --recursive [options] directory

Tidy tool can be used to clean up and change format of Robot Framework test
data files. The output is written into the standard output stream by default,
but an optional output file can be given starting from Robot Framework 2.7.5.
Files can also be modified in-place using --inplace or --recursive options.

Options
=======

 -i --inplace    Tidy given file(s) so that original file(s) are overwritten
                 (or removed, if the format is changed). When this option is
                 used, it is possible to give multiple input files.
                 Examples:
                   python -m robot.tidy --inplace tests.html
                   python -m robot.tidy --inplace --format txt *.html
 -r --recursive  Process given directory recursively. Files in the directory
                 are processed in-place similarly as when --inplace option
                 is used.
 -f --format txt|html|tsv|robot
                 Output file format. If omitted, the format of the input
                 file is used.
 -p --usepipes   Use pipe (`|`) as a cell separator in the txt format.
 -s --spacecount number
                 The number of spaces between cells in the txt format.
                 New in Robot Framework 2.7.3.
 -l --lineseparator native|windows|unix
                 Line separator to use in outputs. The default is 'native'.
                 native:  use operating system's native line separators
                 windows: use Windows line separators (CRLF)
                 unix:    use Unix line separators (LF)
                 New in Robot Framework 2.7.6.
 -h -? --help    Show this help.

Cleaning up the test data
=========================

Test case files created with HTML editors or written by hand can be normalized
using Tidy. Tidy always writes consistent headers, consistent order for
settings, and consistent amount of whitespace between cells and tables.

Examples:
  python -m robot.tidy messed_up_tests.html cleaned_tests.html
  python -m robot.tidy --inplace tests.txt

Changing the test data format
=============================

Robot Framework supports test data in HTML, TSV and TXT formats, and Tidy
makes changing between the formats trivial. Input format is always determined
based on the extension of the input file. Output format is got from the
extension of the output file, when used, and can also be set using the --format
option.

Examples:
  python -m robot.tidy tests.html tests.tsv
  python -m robot.tidy --format tsv --inplace tests.html
  python -m robot.tidy --format txt --recursive mytests

Output encoding
===============

All output files are written using UTF-8 encoding. Outputs written to the
console use the current console encoding.

Alternative execution
=====================

In the above examples Tidy is used only with Python, but it works also with
Jython and IronPython. Above it is executed as an installed module, but it
can also be run as a script like `python path/robot/tidy.py`.

For more information about Tidy and other built-in tools, see
http://robotframework.org/robotframework/#built-in-tools.
"""


class Tidy(object):
    """Programmatic API for the `Tidy` tool.

    Arguments accepted when creating an instance have same semantics as
    Tidy command line options with same names.
    """

    def __init__(self, format='txt', use_pipes=False,
                 space_count=4, line_separator=os.linesep):
        self._options = dict(format=format,
                             pipe_separated=use_pipes,
                             txt_separating_spaces=space_count,
                             line_separator=line_separator)

    def file(self, path, output=None):
        """Tidy a file.

        :param path: Path of the input file.
        :param output: Path of the output file. If not given, output is
            returned.

        Use :func:`inplace` to tidy files in-place.
        """
        data = self._parse_data(path)
        with self._get_writer(path, output) as writer:
            self._save_file(data, writer)
            if not output:
                return writer.getvalue().replace('\r\n', '\n')

    def _get_writer(self, inpath, outpath):
        if PY2 and self._is_tsv(inpath):
            return binary_file_writer(outpath)
        return file_writer(outpath, newline=self._options['line_separator'])

    def _is_tsv(self, path):
        format = self._options['format'] or os.path.splitext(path)[1][1:]
        return format.upper() == 'TSV'

    def inplace(self, *paths):
        """Tidy file(s) in-place.

        :param paths: Paths of the files to to process.
        """
        for path in paths:
            self._save_file(self._parse_data(path))

    def directory(self, path):
        """Tidy a directory.

        :param path: Path of the directory to process.

        All files in a directory, recursively, are processed in-place.
        """
        self._save_directory(self._parse_data(path))

    @disable_curdir_processing
    def _parse_data(self, path):
        if os.path.isdir(path):
            return TestDataDirectory(source=path).populate()
        if self._is_init_file(path):
            path = os.path.dirname(path)
            return TestDataDirectory(source=path).populate(recurse=False)
        try:
            return TestCaseFile(source=path).populate()
        except DataError:
            try:
                return ResourceFile(source=path).populate()
            except DataError:
                raise DataError("Invalid data source '%s'." % path)

    def _is_init_file(self, path):
        return os.path.splitext(os.path.basename(path))[0].lower() == '__init__'

    def _save_file(self, data, output=None):
        source = data.initfile if self._is_directory(data) else data.source
        if source and not output:
            os.remove(source)
        data.save(output=output, **self._options)

    def _save_directory(self, data):
        if not self._is_directory(data):
            self._save_file(data)
            return
        if data.initfile:
            self._save_file(data)
        for child in data.children:
            self._save_directory(child)

    def _is_directory(self, data):
        return hasattr(data, 'initfile')


class TidyCommandLine(Application):
    """Command line interface for the `Tidy` tool.

    Typically :func:`tidy_cli` is a better suited for command line style
    usage and :class:`Tidy` for other programmatic usage.
    """

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=(1,))

    def main(self, arguments, recursive=False, inplace=False, format='txt',
             usepipes=False, spacecount=4, lineseparator=os.linesep):
        tidy = Tidy(format=format, use_pipes=usepipes,
                    space_count=spacecount, line_separator=lineseparator)
        if recursive:
            tidy.directory(arguments[0])
        elif inplace:
            tidy.inplace(*arguments)
        else:
            output = tidy.file(*arguments)
            self.console(output)

    def validate(self, opts, args):
        validator = ArgumentValidator()
        opts['recursive'], opts['inplace'] \
            = validator.mode_and_arguments(args, **opts)
        opts['format'] = validator.format(args, **opts)
        opts['lineseparator'] = validator.line_sep(**opts)
        if not opts['spacecount']:
            opts.pop('spacecount')
        else:
            opts['spacecount'] = validator.spacecount(opts['spacecount'])
        return opts, args


class ArgumentValidator(object):

    def mode_and_arguments(self, args, recursive, inplace, **others):
        recursive, inplace = bool(recursive), bool(inplace)
        validators = {(True, True): self._recursive_and_inplace_together,
                      (True, False): self._recursive_mode_arguments,
                      (False, True): self._inplace_mode_arguments,
                      (False, False): self._default_mode_arguments}
        validator = validators[(recursive, inplace)]
        validator(args)
        return recursive, inplace

    def _recursive_and_inplace_together(self, args):
        raise DataError('--recursive and --inplace can not be used together.')

    def _recursive_mode_arguments(self, args):
        if len(args) != 1:
            raise DataError('--recursive requires exactly one argument.')
        if not os.path.isdir(args[0]):
            raise DataError('--recursive requires input to be a directory.')

    def _inplace_mode_arguments(self, args):
        if not all(os.path.isfile(path) for path in args):
            raise DataError('--inplace requires inputs to be files.')

    def _default_mode_arguments(self, args):
        if len(args) not in (1, 2):
            raise DataError('Default mode requires 1 or 2 arguments.')
        if not os.path.isfile(args[0]):
            raise DataError('Default mode requires input to be a file.')

    def format(self, args, format, inplace, recursive, **others):
        if not format:
            if inplace or recursive or len(args) < 2:
                return None
            format = os.path.splitext(args[1])[1][1:]
        format = format.upper()
        if format not in ('TXT', 'TSV', 'HTML', 'ROBOT'):
            raise DataError("Invalid format '%s'." % format)
        return format

    def line_sep(self, lineseparator, **others):
        values = {'native': os.linesep, 'windows': '\r\n', 'unix': '\n'}
        try:
            return values[(lineseparator or 'native').lower()]
        except KeyError:
            raise DataError("Invalid line separator '%s'." % lineseparator)

    def spacecount(self, spacecount):
        try:
            spacecount = int(spacecount)
            if spacecount < 2:
                raise ValueError
        except ValueError:
            raise DataError('--spacecount must be an integer greater than 1.')
        return spacecount


def tidy_cli(arguments):
    """Executes `Tidy` similarly as from the command line.

    :param arguments: Command line arguments as a list of strings.

    Example::

        from robot.tidy import tidy_cli

        tidy_cli(['--format', 'txt', 'tests.html'])
    """
    TidyCommandLine().execute_cli(arguments)


if __name__ == '__main__':
    tidy_cli(sys.argv[1:])
