Robot Framework
===============

Introduction
------------

`Robot Framework <http://robotframework.org>`__ is a generic test automation
framework for acceptance testing and acceptance test-driven development (ATDD).
It has easy-to-use tabular test data syntax and it utilizes the keyword-driven
testing approach. Its testing capabilities can be extended by test libraries
implemented either with Python or Java, and users can create new higher-level
keywords from existing ones using the same syntax that is used for creating
test cases.

Robot Framework is operating system and application independent. The core
framework is implemented using `Python <http://python.org>`__ and runs also on
`Jython <http://jython.org>`__ (JVM) and `IronPython <http://ironpython.net>`__
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
.. _pip: http://pip-installer.org

Installation
------------

If you already have Python with pip_ installed, you can simply run::

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
line usage. For a complete reference manual see `Robot Framework User Guide`__.

__ http://robotframework.org/robotframework/#user-guide

License
-------

Robot Framework code is provided under `Apache License 2.0`__. Documentation
and other similar content use `Creative Commons Attribution 3.0 Unported`__
license. Most libraries and tools in the ecosystem are also open source, but
they may use different licenses.

__ http://apache.org/licenses/LICENSE-2.0
__ http://creativecommons.org/licenses/by/3.0
