.. _tidy:

Test data clean-up tool (Tidy)
==============================

.. contents::
   :depth: 1
   :local:

Tidy is Robot Framework's built-in a tool for cleaning up and changing
the format of Robot Framework test data files.

The output is written into the standard output stream by default, but
an optional output file can be given as well. Files can also be modified
in-place using :option:`--inplace` or :option:`--recursive` options.

General usage
-------------

Synopsis
~~~~~~~~

::

    python -m robot.tidy [options] inputfile
    python -m robot.tidy [options] inputfile [outputfile]
    python -m robot.tidy --inplace [options] inputfile [more input files]
    python -m robot.tidy --recursive [options] directory

Options
~~~~~~~

 -i, --inplace    Tidy given file(s) so that original file(s) are overwritten
                  (or removed, if the format is changed). When this option is
                  used, it is possible to give multiple input files. Examples::

                      python -m robot.tidy --inplace tests.robot
                      python -m robot.tidy --inplace --format robot *.html

 -r, --recursive  Process given directory recursively. Files in the directory
                  are processed in place similarly as when :option:`--inplace`
                  option is used. Does not process referenced resource files.
 -f, --format <robot|txt|html|tsv>
                  Output file format. If the output file is given explicitly,
                  the default value is got from its extension. Otherwise
                  the format is not changed.
 -p, --use-pipes  Use a pipe character (|) as a cell separator in the plain
                  text format.
 -s, --spacecount <number>
                  The number of spaces between cells in the plain text format.
                  Default is 4.
 -l, --lineseparator <native|windows|unix>
                  Line separator to use in outputs. The default is 'native'.

                  - *native*: use operating system's native line separators
                  - *windows*: use Windows line separators (CRLF)
                  - *unix*: use Unix line separators (LF)

 -h, --help       Show this help.

Alternative execution
~~~~~~~~~~~~~~~~~~~~~

Although Tidy is used only with Python in the synopsis above, it works
also with Jython and IronPython. In the synopsis Tidy is executed as
an installed module (`python -m robot.tidy`), but it can be run also as
a script::

    python path/robot/tidy.py [options] arguments

Executing as a script can be useful if you have done `manual installation`_
or otherwise just have the :file:`robot` directory with the source code
somewhere in your system.

Output encoding
~~~~~~~~~~~~~~~

All output files are written using UTF-8 encoding. Outputs written to the
console use the current console encoding.

Cleaning up test data
---------------------

Test case files can be normalized using Tidy. Tidy always writes consistent
headers, consistent order for settings, and consistent amount of whitespace
between sections and cells.

Examples::

    python -m robot.tidy messed_up_tests.robot cleaned_up_tests.robot
    python -m robot.tidy --inplace tests.robot
    python -m robot.tidy --recursive path/to/tests

Changing test data format
-------------------------

Robot Framework supports test data in `various formats`__, but nowadays the
plain text format with the :file:`.robot` extension is the most commonly used.
Tidy makes it easy to convert data from one format to another. This is
especially useful if there is a need to convert tests in deprecated `HTML
format`_ to other formats.

Input format is always determined based on the extension of the input file.
If output file is given, the output format is got from its extension.
When using :option:`--inplace` or :option:`--recursive`, it is possible to
specify the desired format using the :option:`--format` option.

Examples::

    python -m robot.tidy tests.html tests.robot
    python -m robot.tidy --format robot --inplace tests.html
    python -m robot.tidy --format robot --recursive path/to/tests

__ `Supported file formats`_
