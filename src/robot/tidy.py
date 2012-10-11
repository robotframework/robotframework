#!/usr/bin/env python

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

USAGE = """robot.tidy -- Robot Framework test data clean-up tool.

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
 -f --format txt|html|tsv
                 Output file format. If omitted, the format of the input
                 file is used.
 -p --usepipes   Use pipe (`|`) as a cell separator in the txt format.
 -s --spacecount number
                 The number of spaces between cells in the txt format.
                 New in Robot Framework 2.7.3.
 -h -? --help    Show this help.

Cleaning up the test data
=========================

Test case files created with HTML editors or written by hand can be normalized
using tidy. Tidy always writes consistent headers, consistent order for
settings, and consistent amount of whitespace between cells and tables.

Examples:
  python -m robot.tidy messed_up_tests.html cleaned_tests.html
  python -m robot.tidy --inplace tests.txt

Changing the test data format
=============================

Robot Framework supports test data in HTML, TSV and TXT formats and this tool
makes changing between the formats trivial. Input format is always determined
based on the extension of the input file. Output format can be set using
the --format option.

Examples:
  python -m robot.tidy --format tsv --inplace tests.html
  python -m robot.tidy --format txt --recursive mytests

Output encoding
===============

All output files are written using UTF-8 encoding. Outputs written to the
console use the current console encoding.

Alternative execution
=====================

In the above examples tidy is used only with Python, but it works also with
Jython and IronPython. Above tidy is executed as an installed module, but
it can also be executed as a script like `python path/robot/tidy.py`.
"""

import os
import sys
from StringIO import StringIO

# Allows running as a script. __name__ check needed with multiprocessing:
# http://code.google.com/p/robotframework/issues/detail?id=1137
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter

from robot.errors import DataError
from robot.parsing import (ResourceFile, TestDataDirectory, TestCaseFile,
                           disable_curdir_processing)
from robot.utils import Application


class Tidy(object):

    def __init__(self, **options):
        self._options = options

    def file(self, path, output=None):
        data = self._create_datafile(path)
        outfile = open(output, 'w') if output else StringIO()
        try:
            self._save_file(data, outfile)
            if not output:
                return outfile.getvalue().replace('\r\n', '\n').decode('UTF-8')
        finally:
            outfile.close()

    def directory(self, path):
        self._save_directory(TestDataDirectory(source=path).populate())

    def inplace(self, path):
        self._save_file(self._create_datafile(path))

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

    @disable_curdir_processing
    def _create_datafile(self, source):
        if self._is_init_file(source):
            dir_ = os.path.dirname(source)
            return TestDataDirectory(source=dir_).populate(recurse=False)
        try:
            return TestCaseFile(source=source).populate()
        except DataError:
            try:
                return ResourceFile(source=source).populate()
            except DataError:
                raise DataError("Invalid data source '%s'." % source)

    def _is_init_file(self, source):
        return os.path.splitext(os.path.basename(source))[0] == '__init__'


class TidyCommandLine(Application):

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=(1,))

    def main(self, arguments, recursive=False, inplace=False, format='txt',
             usepipes=False, spacecount=4):
        tidy = Tidy(format=format, pipe_separated=usepipes,
                    txt_separating_spaces=spacecount)
        if recursive:
            tidy.directory(arguments[0])
        elif inplace:
            for source in arguments:
                tidy.inplace(source)
        else:
            output = tidy.file(*arguments)
            self.console(output)

    def validate(self, opts, args):
        self._validate_mode_and_arguments(args, **opts)
        opts['format'] = self._validate_format(args, **opts)
        if not opts['spacecount']:
            opts.pop('spacecount')
        else:
            opts['spacecount'] = self._validate_spacecount(opts['spacecount'])
        return opts, args

    def _validate_mode_and_arguments(self, args, inplace, recursive, **others):
        if inplace and recursive:
            raise DataError('--recursive and --inplace can not be used together.')
        if recursive and (len(args) > 1 or not os.path.isdir(args[0])):
            raise DataError('--recursive requires exactly one directory as argument.')
        if not (inplace or recursive) and len(args) > 2:
            raise DataError('Default mode requires 1 or 2 arguments.')

    def _validate_format(self, args, format, inplace, recursive, **others):
        if not format:
            if inplace or recursive or len(args) < 2:
                return None
            format = os.path.splitext(args[1])[1][1:]
        format = format.upper()
        if format not in ['TXT', 'TSV', 'HTML']:
            raise DataError("Invalid format: '%s'." % format)
        return format

    def _validate_spacecount(self, spacecount):
        try:
            spacecount = int(spacecount)
            if spacecount < 2:
                raise ValueError
        except ValueError:
            raise DataError('--spacecount must be an integer greater than 1.')
        return spacecount


def tidy_cli(args):
    """Executes tidy similarly as from the command line.

    :param args: command line arguments as a list of strings.

    Example:
        tidy_cli(['--format', 'txt', 'mytests.html'])
    """
    TidyCommandLine().execute_cli(args)


if __name__ == '__main__':
    tidy_cli(sys.argv[1:])
