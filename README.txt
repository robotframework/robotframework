This is an unofficial Robot Framework Python 3.x compatibility fork.
It also remains compatible with all officially supported
Python 2.x platforms and versions, starting with 2.5.

It uses the ``2to3`` tool in ``setup.py`` and ``atest/run_atests.py``.
The latter copies ``src/robot/`` and ``atest/`` to ``atest/python3/``
before running the ``2to3`` script on them
and also converts some contents
of the Test Suite and Resource ``.txt`` files.

``2to3`` can't handle everything...
Some fixers are disabled and there are also manual code changes.
The latter are mostly commented, with ``Python 3`` in the text,
or contain ``if sys.version_info[0] == 3``.
Manually changes in the acceptance Test Suites and Resources
mostly use ``Run on python 2.x`` and ``3.x`` Keywords for switching.

You can also look at this URL for a complete diff:

https://bitbucket.org/userzimmermann/robotframework-python3/compare/default..853a2e8#diff

Most of the acceptance tests are already passing with Python 3.
Only ``57/3164`` critical tests are currently failing on my machine,
but this is mostly related to the tests themselves,
which need some further workarounds, switches and conversions.

-- Stefan Zimmermann


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


License
-------

Robot Framework code and tests are provided under Apache License 2.0.
Documentation and other similar content use Creative Commons
Attribution 3.0 Unported license.

 - http://apache.org/licenses/LICENSE-2.0
 - http://creativecommons.org/licenses/by/3.0


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

