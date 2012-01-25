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

"""robot.tidy -- Robot Framework test data clean-up tool.

Usage: python -m robot.tidy [options] inputfile
   or: python -m robot.tidy [options] inputfile > outputfile
   or: python -m robot.tidy --inplace [options] inputfile [more input files]
   or: python -m robot.tidy --recursive [options] directory

This tool can be used to clean up and change format of Robot Framework test
data files. By default, the output is written to the standard output stream,
but it can be redirected to a file. Alternatively, files can be modified
in-place using --inplace or --recursive options.

Options:
 -i --inplace    Tidy given file(s) so that original file(s) are overwritten
                 (or removed, if the format is changed). When this option is
                 used, it is possible to give multiple input files.
                 Examples:
                   python -m robot.tidy --inplace tests.html
                   python -m robot.tidy --inplace --format txt *.html
 -r --recursive  Process given directory recursively. Files in the directory
                 are processed in place similarly as when --inplace option is
                 used.
 -f --format txt|html|tsv
                 Output file format. If omitted, the format of the input
                 file is used.
 -p --use-pipes  Use pipe (`|`) as a cell separator in the txt format.
 -h --help       Show this help.

Cleaning up the test data
=========================

Test case files created with HTML editors or written by hand can be normalized
using tidy. Tidy always writes consistent headers, consistent order for
settings, and consistent amount of whitespace between cells and tables.

Examples:
  python -m robot.tidy messed_up_tests.html > cleaned_tests.html
  python -m robot.tidy --inplace tests.txt

Changing the test data format
=============================

Robot Framework supports test data in HTML, TSV and TXT formats and this tool
makes changing between the formats trivial. Input format is always determined
based on the extension of the input file. Output format can be set using
the --format option.

Examples:
  python -m robot.tidy --format tsv tests_in_html.html > tests_in_tsv.tsv
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

if 'robot' not in sys.modules:
    import pythonpathsetter   # running tidy.py as script

from robot import utils
from robot.errors import DataError, Information
from robot.parsing import ResourceFile, TestDataDirectory, TestCaseFile
from robot.parsing.populators import FromFilePopulator


class Tidy(object):

    def __init__(self, **options):
        self._options = options

    def file(self, path):
        output = StringIO()
        data = self._create_datafile(path)
        data.save(output=output, **self._options)
        return output.getvalue().decode('UTF-8')

    def directory(self, path):
        self._save_directory(TestDataDirectory(source=path).populate())

    def inplace(self, path):
        self._save_file(self._create_datafile(path))

    def _save_file(self, data):
        source = data.initfile if self._is_directory(data) else data.source
        if source:
            os.remove(source)
        data.save(**self._options)

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


class TidyCommandLine(object):

    def __init__(self, usage):
        self._parser = utils.ArgumentParser(usage)

    def run(self, args):
        options, inputs = self._parse_args(args)
        tidy = Tidy(format=options['format'],
                    pipe_separated=options['use-pipes'])
        if options['recursive']:
            tidy.directory(inputs[0])
        elif options['inplace']:
            for source in inputs:
                tidy.inplace(source)
        else:
            return tidy.file(inputs[0])

    def _parse_args(self, args):
        options, sources = self._parser.parse_args(args, help='help')
        if options['inplace'] and options['recursive']:
            raise DataError('--recursive and --inplace can not be used together.')
        if not options['inplace'] and len(sources) > 1:
            raise DataError('Expected exactly 1 input file.')
        if not sources:
            raise DataError('Expected at least 1 input file.')
        if options['recursive'] and not os.path.isdir(sources[0]):
            raise DataError('--recursive requires input to be a directory.')
        format = options['format']
        if format and format not in ['txt', 'tsv', 'html']:
            raise DataError("Invalid format: %s." % format)
        return options, sources


def console(msg):
    if sys.stdout.isatty():
        msg = utils.encode_output(msg)
    else:
        if os.sep == '\\' and 'b' not in sys.stdout.mode:
            msg = msg.replace('\r\n', '\n')
        msg = msg.encode('UTF-8')
    sys.stdout.write(msg)


if __name__ == '__main__':
    try:
        output = TidyCommandLine(__doc__).run(sys.argv[1:])
        if output:
            console(output)
    except DataError, err:
        console('%s\n\nUse --help for usage.' % unicode(err))
        sys.exit(1)
    except Information, msg:
        console(unicode(msg))
    sys.exit(0)
