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
framework is implemented using `Python <http://python.org>`_, supports both
Python 2 and Python 3, and runs also on `Jython <http://jython.org>`_ (JVM)
and `IronPython <http://ironpython.net>`_ (.NET). The framework has a rich
ecosystem around it consisting of various generic test libraries and tools
that are developed as separate projects. For more information about Robot
Framework and the ecosystem, see http://robotframework.org.

Robot Framework project is hosted on GitHub_ where you can find source code,
an issue tracker, and some further documentation. See `<CONTRIBUTING.rst>`__
if you are interested to contribute. Downloads are hosted on PyPI_, except
for the standalone JAR distribution that is on `Maven central`_.

Robot Framework development is sponsored by `Robot Framework Foundation
<http://robotframework.org/foundation>`_.

.. _GitHub: https://github.com/robotframework/robotframework
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _Maven central: http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework

.. image:: https://img.shields.io/pypi/v/robotframework.svg?label=version
   :target: https://pypi.python.org/pypi/robotframework
   :alt: Latest version

.. image:: https://img.shields.io/pypi/dm/robotframework.svg
   :target: https://pypi.python.org/pypi/robotframework
   :alt: Number of downloads

.. image:: https://img.shields.io/pypi/l/robotframework.svg
   :target: http://www.apache.org/licenses/LICENSE-2.0.html
   :alt: License

.. image:: https://robotframework-slack.herokuapp.com/badge.svg
   :target: https://robotframework-slack.herokuapp.com
   :alt: Slack channel

Installation
------------

If you already have Python_ with `pip <http://pip-installer.org>`_ installed,
you can simply run::

    pip install robotframework

Alternatively you can get Robot Framework source code by downloading the source
distribution from PyPI_ and extracting it, or by cloning the project repository
from GitHub_. After that you can install the framework with::

    python setup.py install

For more detailed installation instructions, including installing
Python, Jython and IronPython, see `<INSTALL.rst>`__.

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
    Resource          resource.robot

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

Starting from Robot Framework 3.0, tests are executed from the command line
using the ``robot`` script or by executing the ``robot`` module directly
like ``python -m robot`` or ``jython -m robot``. Older Robot Framework
versions have Python interpreter specific ``pybot``, ``jybot`` and ``ipybot``
scripts that still work but will be deprecated and removed in the future.

The basic usage is giving a path to a test case file or directory as an
argument with possible command line options before the path::

    robot tests.robot
    robot --variable HOST:example.com --outputdir results path/to/tests/

Additionally there is ``rebot`` tool for combining results and otherwise
post-processing outputs::

    rebot --name Example output1.xml output2.xml

Run ``robot --help`` and ``rebot --help`` for more information about the command
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

Support and contact
-------------------

- `robotframework-users
  <https://groups.google.com/group/robotframework-users/>`_ mailing list
- `Slack <https://robotframework-slack.herokuapp.com>`_ community
- `#robotframework <http://webchat.freenode.net/?channels=robotframework&prompt=1>`_
  IRC channel on freenode
- `@robotframework <https://twitter.com/robotframework>`_ on Twitter
- `Other forums <http://robotframework.org/#support-contact>`_

License
-------

Robot Framework is open source software provided under the `Apache License
2.0`__. Robot Framework documentation and other similar content use the
`Creative Commons Attribution 3.0 Unported`__ license. Most libraries and tools
in the ecosystem are also open source, but they may use different licenses.

__ http://apache.org/licenses/LICENSE-2.0
__ http://creativecommons.org/licenses/by/3.0
