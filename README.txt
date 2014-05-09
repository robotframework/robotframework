Robot Framework with Python 3.3+ compatibility
==============================================

https://bitbucket.org/userzimmermann/robotframework-python3

- Forked from https://robotframework.googlecode.com
- Compatible with **Python 2.7**

Please report any issues to:

https://bitbucket.org/userzimmermann/robotframework-python3/issues

You can look at this URL for a complete code diff:

https://bitbucket.org/userzimmermann/robotframework-python3/compare/master..robot#diff


Installation
------------

::

    python setup.py install

Or with `pip <http://www.pip-installer.org>`_::

    pip install .

Or from `PyPI <https://pypi.python.org/pypi/robotframework-python3>`_::

    pip install robotframework-python3

Requirements
............

* `six <https://pypi.python.org/pypi/six>`_


Differences in Python 3
-----------------------

Python 3 makes a clear distinction between *str* for textual data
and *bytes* for binary data.
This affects the Standard Test Libraries and their Keywords:

- *str* arguments don't work where *bytes* are expected,
  like writing to binary file streams or comparing with other *bytes*.
- *bytes* don't work where *str* is expected,
  like writing to text mode streams or comparing with another *str*.
- Reading from binary streams always returns *bytes*.
- Reading from text streams always returns *str*.

You can use the following keywords to explicitly create *bytes*:

- **BuiltIn.Convert To Bytes**
- **String.Encode String To Bytes**

I extended **Process.Start Process** with a *binary_mode* argument.
By default the process streams are opened in text mode.
You can change this with::

    binary_mode=True

**Collections.Get Dictionary Keys** normally sorts the keys.
I disabled key sorting in Python 3,
because most builtin types are not comparable to each other.
This further affects **Get Dictionary Values** and **Get Dictionary Items**.
I still need to find a better solution... Maybe imitate Python 2 sorting?
Any suggestions? :)


-- **Stefan Zimmermann**


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

