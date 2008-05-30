Robot Framework
===============

1. Introduction
---------------

Robot Framework is a keyword-driven test automation framework with an
easy-to-use tabular syntax for creating test cases. Test data can be
either in HTML or TSV format. Robot's testing capabilities can be
easily extended by test libraries having a very simple API. Libraries
can be implemented either with Python or Java (requires Jython). Users
can also create new keywords from existing ones using the same simple
syntax that is used for creating test cases.

Robot Framework has two start-up scripts, 'pybot' and 'jybot', which
run it on Python and Jython interpreters, respectively. Alternatively
it is possible to directly call robot/runner.py script using selected
interpreter. Additionally there's a 'rebot' tool that can be used to
combine and recreate reports and logs from Robot Framework's XML
output files.

Data sources given to Robot Framework are either test case files or
directories containing them and/or other directories. Single test case
file creates a test suite containing all the test cases in it and a
directory containing test case files creates a higher level test suite
with test case files or other directories as sub test suites. If
multiple data sources are given, a virtual test suite containing
suites generated from given data sources is created.


2. More Information
-------------------

Robot Framework documentation including User Guide and keyword
documentations of standard libraries can be found from 'doc'
directory. For more information e.g. about external test libraries go
to http://robotframework.org.


3. Installation
---------------

See INSTALLATION.txt for installation and uninstallation instructions.

Additionally PACKAGING.tx contains details about creating new
installation packages.


4. Directory Layout
-------------------

atest/
    Acceptance tests. Naturally using Robot Framework.

devscripts/
    Helper scripts for Robot Framework developers.

doc/
    User Guide and standard library documentation.

proto/
    Tools, scripts, etc. not yet ready for real use.

src/
    Robot Framework source code.

templates/
    Simple HTML and TSV test data templates.

tools/
    Different utilities for Robot Framework users.

utest/
    Unit tests.

