.. _tidy:

Test data clean-up tool (Tidy)
==============================

.. contents::
   :depth: 1
   :local:

Tidy tool can be used to clean up Robot Framework data. It, for example, uses
headers and settings consistently and adds consistent amount of whitespace
between sections, keywords and their arguments, and other pieces of the data.
It also converts old syntax to new syntax when appropriate.

When tidying a single file, the output is written to the console by default,
but an optional output file can be given as well. Files can also be modified
in-place using :option:`--inplace` or :option:`--recursive` options.

General usage
-------------

Synopsis
~~~~~~~~

::

    python -m robot.tidy [options] input
    python -m robot.tidy [options] input [output]
    python -m robot.tidy --inplace [options] input [more inputs]
    python -m robot.tidy --recursive [options] directory

Options
~~~~~~~

 -i, --inplace    Tidy given file(s) so that original file(s) are overwritten.
                  When this option is used, it is possible to give multiple
                  input files.
 -r, --recursive  Process given directory recursively. Files in the directory
                  are processed in place similarly as when :option:`--inplace`
                  option is used. Does not process referenced resource files.
 -p, --usepipes   Use a pipe character (`|`) as a column separator in the plain
                  text format.
 -s, --spacecount <number>
                  The number of spaces between cells in the plain text format.
                  Default is 4.
 -l, --lineseparator <native|windows|unix>
                  Line separator to use in outputs. The default is *native*.

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

Examples
--------

::

    python -m robot.tidy example.robot
    python -m robot.tidy messed_up_data.robot cleaned_up_data.robot
    python -m robot.tidy --inplace example.robot
    python -m robot.tidy --recursive path/to/tests

Deprecation
-----------

The built-in Tidy tool was deprecated in Robot Framework 4.1 in favor of the
new and enhanced external Robotidy__ tool. The built-in tool will be removed
altogether in Robot Framework 5.0.

__ https://robotidy.readthedocs.io/
