.. _tidy:

Test data clean-up tool (:prog:`tidy`)
--------------------------------------

.. contents::
   :depth: 1
   :local:

:prog:`tidy` is a tool for cleaning up and changing the format of Robot
Framework test data files. It is built-in into Robot Framework and
automatically included in the installation starting from version 2.7.

The output is written into the standard output stream by default, but
an optional output file can be given starting from Robot Framework 2.7.5.
Files can also be modified in-place using :opt:`--inplace` or
:opt:`--recursive` options.

General usage
~~~~~~~~~~~~~

Synopsis
''''''''

::

    python -m robot.tidy [options] inputfile
    python -m robot.tidy [options] inputfile [outputfile]
    python -m robot.tidy --inplace [options] inputfile [more input files]
    python -m robot.tidy --recursive [options] directory

Options
'''''''

 -i, --inplace    Tidy given file(s) so that original file(s) are overwritten
                  (or removed, if the format is changed). When this option is
                  used, it is possible to give multiple input files. Examples::

                      python -m robot.tidy --inplace tests.html
                      python -m robot.tidy --inplace --format txt *.html

 -r, --recursive  Process given directory recursively. Files in the directory
                  are processed in place similarly as when :opt:`--inplace`
                  option is used.
 -f, --format <txt|html|tsv>
                  Output file format. If the output file is given explicitly,
                  the default value is got from its extension. Otherwise
                  the format is not changed.
 -p, --use-pipes  Use a pipe character (|) as a cell separator in the txt format.
 -s, --spacecount <number>
                  The number of spaces between cells in the txt format.
                  New in Robot Framework 2.7.3.
 -h, --help       Show this help.

Alternative execution
'''''''''''''''''''''

Although :prog:`tidy` is used only with Python in the synopsis above, it works
also with Jython and IronPython. In the synopsis :prog:`tidy` is executed as
an installed module (:cli:`python -m robot.tidy`), but it can be run also as
a script::

    python path/robot/tidy.py [options] arguments

Executing as a script can be useful if you have done `manual installation`_
or otherwise just have the :path:`robot` directory with the source code
somewhere in your system.

Output encoding
'''''''''''''''

All output files are written using UTF-8 encoding. Outputs written to the
console use the current console encoding.

Cleaning up test data
~~~~~~~~~~~~~~~~~~~~~

Test case files created with HTML editors or written by hand can be normalized
using tidy. :prog:`tidy` always writes consistent headers, consistent order for
settings, and consistent amount of whitespace between cells and tables.

Examples::

    python -m robot.tidy messed_up_tests.html cleaned_tests.html
    python -m robot.tidy --inplace tests.txt

Changing test data format
~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework supports test data in HTML, TSV and TXT formats and :prog:`tidy`
makes changing between the formats trivial. Input format is always determined
based on the extension of the input file. Output format can be set using
the :opt:`--format` option, and the default value is got from the extension
of the possible output file.

Examples::

    python -m robot.tidy tests.html tests.txt
    python -m robot.tidy --format txt --inplace tests.html
    python -m robot.tidy --format tsv --recursive mytests
