Robot Framework
===============

Introduction
------------

Robot Framework is a Python-based keyword-driven test automation framework 
with an easy-to-use tabular syntax for creating test cases. Its testing 
capabilities can be extended by test libraries implemented either with Python 
or Java.  Users can also create new keywords from existing ones using the same 
simple syntax that is used for creating test cases.

  - Enables easy-to-use tabular syntax for creating test cases in a uniform
    way.
  - Provides ability to create reusable higher-level keywords from the
    existing keywords.
  - Provides easy-to-read result reports and logs in HTML format.
  - Is platform and application independent.
  - Can natively use both Python and Java test code.
  - Provides a simple library API for creating customized test libraries.
  - Provides a command line interface and XML based outputs for integration
    into existing build infrastructure (continuous integration systems).
  - Provides support for Selenium for web testing, Java GUI testing, running
    processes, Telnet, SSH, and so on.
  - Supports creating data-driven tests.
  - Provides tagging to categorize and select test cases to be executed. 

Robot Framework documentation including User Guide and keyword
documentations of standard libraries can be found from 'doc'
directory. For more information, see http://robotframework.org.


Installation
------------

See INSTALLATION.txt for installation and uninstallation instructions.

Additionally PACKAGING.tx contains details about creating new
installation packages.


Usage
-----

Robot Framework is executed from command line using `pybot` or `jybot`
runner scripts, which run the framework with Python or Jython interpreters,
respectively. The basic usage is giving a path to test data to be executed as
an argument to the selected runner, with possible command line options before
the path. Additionally there is a `rebot` tool for post-processing outputs.

Examples::

  pybot mytests.html
  jybot --variable HOST:myhost --outputdir results path/to/tests/
  rebot --name Example output1.xml output2.xml


For more information, run `pybot --help` and `rebot --help` or see the 
user guide.


Directory Layout
----------------

atest/
    Acceptance tests. Naturally using Robot Framework.

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

