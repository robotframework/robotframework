Robot Framework with Python 3.3+ compatibility
==============================================

https://github.com/userzimmermann/robotframework/tree/python3

- Forked from https://github.com/robotframework/robotframework
- Compatible with **Python 2.7**

Please report any issues to:

https://github.com/userzimmermann/robotframework/issues

You can look at this URL for a complete code diff:

https://github.com/userzimmermann/robotframework/compare/master...python3


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

.. contents::
   :local:

Introduction
------------

`Robot Framework <http://robotframework.org>`_ is a generic open source test
automation framework for acceptance testing and acceptance test-driven
development (ATDD). It has easy-to-use tabular test data syntax and it utilizes
the keyword-driven testing approach. Its testing capabilities can be extended
by test libraries implemented either with Python or Java, and users can create
new higher-level keywords from existing ones using the same syntax that is used
for creating test cases.

Robot Framework is operating system and application independent. The core
framework is implemented using `Python <http://python.org>`_ and runs also on
`Jython <http://jython.org>`_ (JVM) and `IronPython <http://ironpython.net>`_
(.NET). The framework has a rich ecosystem around it consisting of various
generic test libraries and tools that are developed as separate projects.
For more information about Robot Framework and the ecosystem, see
http://robotframework.org.

Robot Framework project is hosted on GitHub_ where you can find source code,
an issue tracker, and some further documentation.  Downloads are hosted at
PyPI_, except for the standalone JAR distribution that is in `Maven central`_.

.. _GitHub: https://github.com/robotframework/robotframework
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _Maven central: http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework

.. image:: https://pypip.in/version/robotframework/badge.png?text=version
   :target: https://pypi.python.org/pypi/robotframework/
   :alt: Latest version

.. image:: https://pypip.in/download/robotframework/badge.png
   :target: https://pypi.python.org/pypi/robotframework/
   :alt: Number of downloads

.. image:: https://pypip.in/license/robotframework/badge.png
   :target: http://www.apache.org/licenses/LICENSE-2.0.html
   :alt: License

Installation
------------

If you already have Python_ with `pip <http://pip-installer.org>`_ installed,
you can simply run::

    pip install robotframework

Alternatively you can get Robot Framework source code by downloading the source
distribution from PyPI_ or cloning the project from GitHub_. After that you can
install the framework with::

    python setup.py install

For more detailed installation instructions, including installing
Python, Jython and IronPython, see `<INSTALL.rst>`__.

.. setup.py replaces the above `<INSTALL.rst>`__ with an absolute URL

Example
-------

Below is a simple example test case for testing login to some system.
You can find more examples with links to related demo projects from
http://robotframework.org.

.. code:: robotframework

    *** Settings ***
    Documentation     A test suite with a single test for valid login.
    ...
    ...               This test has a workflow that is created using keywords in
    ...               the imported resource file.
    Resource          resource.txt

    *** Test Cases ***
    Valid Login
        Open Browser To Login Page
        Input Username    demo
        Input Password    mode
        Submit Credentials
        Welcome Page Should Be Open
        [Teardown]    Close Browser

Usage
-----

Robot Framework is executed from the command line using ``pybot``, ``jybot``
or ``ipybot`` scripts, depending is it run on Python, Jython or IronPython.
The basic usage is giving a path to a test case file or directory as
an argument with possible command line options before the path. Additionally
there is ``rebot`` tool for combining results and otherwise post-processing
outputs::

    pybot tests.txt
    jybot --variable HOST:example.com --outputdir results path/to/tests/
    rebot --name Example output1.xml output2.xml

Run ``pybot --help`` and ``rebot --help`` for more information about the command
line usage. For a complete reference manual see `Robot Framework User Guide`_.

Documentation
-------------

- `Robot Framework User Guide
  <http://robotframework.org/robotframework/#user-guide>`_
- `Standard libraries
  <http://robotframework.org/robotframework/#standard-libraries>`_
- `Built-in tools
  <http://robotframework.org/robotframework/#built-in-tools>`_
- `API documentation
  <http://robot-framework.readthedocs.org>`_
- `General documentation and demos
  <http://robotframework.org/#documentation>`_

License
-------

Robot Framework is open source software provided under under `Apache License
2.0`__. Robot Framework documentation and other similar content use `Creative
Commons Attribution 3.0 Unported`__ license. Most libraries and tools in
the ecosystem are also open source, but they may use different licenses.

__ http://apache.org/licenses/LICENSE-2.0
__ http://creativecommons.org/licenses/by/3.0
