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
from robot.parsing import get_model, SuiteStructureBuilder, SuiteStructureVisitor
from robot.tidypkg import Aligner, Cleaner, NewlineNormalizer, SeparatorNormalizer
from robot.utils import Application, file_writer

USAGE = """robot.tidy -- Robot Framework data clean-up tool

Version:  <VERSION>

Usage:  python -m robot.tidy [options] input
   or:  python -m robot.tidy [options] input [output]
   or:  python -m robot.tidy --inplace [options] input [more inputs]
   or:  python -m robot.tidy --recursive [options] directory

Tidy tool can be used to clean up Robot Framework data. It, for example, uses
headers and settings consistently and adds consistent amount of whitespace
between sections, keywords and their arguments, and other pieces of the data.
It also converts old syntax to new syntax when appropriate.

When tidying a single file, the output is written to the console by default,
but an optional output file can be given as well. Files can also be modified
in-place using --inplace and --recursive options.

All output files are written using UTF-8 encoding. Outputs written to the
console use the current console encoding.

Options
=======

 -i --inplace    Tidy given file(s) so that original file(s) are overwritten.
                 When this option is used, it is possible to give multiple
                 input files.
 -r --recursive  Process given directory recursively. Files in the directory
                 are processed in-place similarly as when --inplace option
                 is used. Does not process referenced resource files.
 -p --usepipes   Use pipe ('|') as a column separator in the plain text format.
 -s --spacecount number
                 The number of spaces between cells in the plain text format.
                 Default is 4.
 -l --lineseparator native|windows|unix
                 Line separator to use in outputs. The default is 'native'.
                 native:  use operating system's native line separators
                 windows: use Windows line separators (CRLF)
                 unix:    use Unix line separators (LF)
 -h -? --help    Show this help.

Examples
========

  python -m robot.tidy example.robot
  python -m robot.tidy messed_up_data.robot cleaned_up_data.robot
  python -m robot.tidy --inplace example.robot
  python -m robot.tidy --recursive path/to/tests

Alternative execution
=====================

In the above examples Tidy is used only with Python, but it works also with
Jython and IronPython. Above it is executed as an installed module, but it
can also be run as a script like `python path/robot/tidy.py`.

For more information about Tidy and other built-in tools, see
http://robotframework.org/robotframework/#built-in-tools.

Deprecation
===========

The built-in Tidy tool was deprecated in Robot Framework 4.1 in favor of the
new and enhanced external Robotidy tool. The built-in tool will be removed
altogether in Robot Framework 5.0. Learn more about the new Robotidy tool at
https://robotidy.readthedocs.io/.
"""


class Tidy(SuiteStructureVisitor):
    """Programmatic API for the `Tidy` tool.

    Arguments accepted when creating an instance have same semantics as
    Tidy command line options with same names.
    """

    def __init__(self, space_count=4, use_pipes=False,
                 line_separator=os.linesep):
        sys.stderr.write(
            "The built-in Tidy tool ('robot.tidy') has been deprecated in favor "
            "of the new and enhanced external Robotidy tool. Learn more about "
            "the new tool at https://robotidy.readthedocs.io/.\n"
        )
        self.space_count = space_count
        self.use_pipes = use_pipes
        self.line_separator = line_separator
        self.short_test_name_length = 18
        self.setting_and_variable_name_length = 14

    def file(self, path, outpath=None):
        """Tidy a file.

        :param path: Path of the input file.
        :param outpath: Path of the output file. If not given, output is
            returned.

        Use :func:`inplace` to tidy files in-place.
        """
        with self._get_output(outpath) as writer:
            self._tidy(get_model(path), writer)
            if not outpath:
                return writer.getvalue().replace('\r\n', '\n')

    def _get_output(self, path):
        return file_writer(path, newline='', usage='Tidy output')

    def inplace(self, *paths):
        """Tidy file(s) in-place.

        :param paths: Paths of the files to to process.
        """
        for path in paths:
            model = get_model(path)
            with self._get_output(path) as output:
                self._tidy(model, output)

    def directory(self, path):
        """Tidy a directory.

        :param path: Path of the directory to process.

        All files in a directory, recursively, are processed in-place.
        """
        data = SuiteStructureBuilder().build([path])
        data.visit(self)

    def _tidy(self, model, output):
        Cleaner().visit(model)
        NewlineNormalizer(self.line_separator,
                          self.short_test_name_length).visit(model)
        SeparatorNormalizer(self.use_pipes, self.space_count).visit(model)
        Aligner(self.short_test_name_length,
                self.setting_and_variable_name_length,
                self.use_pipes).visit(model)
        model.save(output)

    def visit_file(self, file):
        self.inplace(file.source)

    def visit_directory(self, directory):
        if directory.init_file:
            self.inplace(directory.init_file)
        for child in directory.children:
            child.visit(self)


class TidyCommandLine(Application):
    """Command line interface for the `Tidy` tool.

    Typically :func:`tidy_cli` is a better suited for command line style
    usage and :class:`Tidy` for other programmatic usage.
    """

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=(1,))

    def main(self, arguments, recursive=False, inplace=False,
             usepipes=False, spacecount=4, lineseparator=os.linesep):
        tidy = Tidy(use_pipes=usepipes, space_count=spacecount,
                    line_separator=lineseparator)
        if recursive:
            tidy.directory(arguments[0])
        elif inplace:
            tidy.inplace(*arguments)
        else:
            output = tidy.file(*arguments)
            self.console(output)

    def validate(self, opts, args):
        validator = ArgumentValidator()
        opts['recursive'], opts['inplace'] = validator.mode_and_args(args,
                                                                     **opts)
        opts['lineseparator'] = validator.line_sep(**opts)
        if not opts['spacecount']:
            opts.pop('spacecount')
        else:
            opts['spacecount'] = validator.spacecount(opts['spacecount'])
        return opts, args


class ArgumentValidator(object):

    def mode_and_args(self, args, recursive, inplace, **others):
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

        tidy_cli(['--spacecount', '2', 'tests.robot'])
    """
    TidyCommandLine().execute_cli(arguments)


if __name__ == '__main__':
    tidy_cli(sys.argv[1:])
