Tools
=====

This directory contains supporting tools that can be used with Robot
Framwork.  These tools help in some common tasks, but are not part of
the core framework.  Most tools show a help text describing their
purpose and usage when they are executed from the command line without
arguments or with '--help' option.


fileviewery
    A graphical tool for monitoring text file. The main usage is monitoring
    Robot Framework's debug files (see --debugfile option) on Windows and
    systems where `tail` command is not available.

libdoc 
    A tool for generating keyword documentation for test libraries and
    resource files. Works for libraries written both in Python and Java.

oneclickinstaller
    An AutoIT script to automatically install Robot Framework and
    its dependencies on a Windows machine.

ristopy
    A tool for genereating graphs from historical output data.

robotdiff
    A tool for comparing results of two or more test runs.

robotidy
    A tool for cleaning up test data files. Allows also converting between
    HTML and TSV formats.

statuschecker
    A tool for checking that tests failed for excpeted reasons and 
    that keywords have correct log messages.

times2csv
    A tool that reads start, end and elapsed times of every test suite,
    test case and keyword from an output file, and writes all the 
    information to a csv file which can be manipulated further with any 
    spreadsheet program.



