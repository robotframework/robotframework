Robot Framework
===============

NOTICE
------

This repository is currently under migration from
http://code.google.com/p/robotframework/. Code and issues ought to be
now migrated, but it will take some time before we get documentation
such as this README and wikis updated.

Robot Framework
===============

`Robot Framework`_ is a generic test automation framework for acceptance
testing and acceptance test-driven development (ATDD). It has easy-to-use
tabular test data syntax and it utilizes the keyword-driven testing
approach. Its testing capabilities can be extended by test libraries
implemented either with Python or Java, and users can create new
higher-level keywords from existing ones using the same syntax that
is used for creating test cases.

Robot Framework project is hosted on GitHub_ where you can find further
documentation, source code, and issue tracker. Downloads are hosted at
PyPI_, except for standalone jar distribution that is in `Maven central`_.
The framework has a rich ecosystem around it consisting of various
generic test libraries and tools that are developed as separate projects.

Robot Framework is operating system and application independent. The core
framework is implemented using Python_ and runs also on Jython_ (JVM) and
IronPython_ (.NET).

For more information about Robot Framework and the ecosystem,
see http://robotframework.org.

.. _Robot Framework: http://robotframework.org
.. _GitHub: https://github.com/robotframework/robotframework
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _Maven central: http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework
.. _Python: http://python.org
.. _Jython: http://jython.org
.. _IronPython: http://ironpython.net

Installation
------------

If you already have Python with pip_ installed, you can simply run::

    pip install robotframework

Otherwise see `INSTALL.rst`_ for detailed installation instructions.
The cover also installing Python, Jython and IronPython.

.. _INSTALL.rst: https://github.com/robotframework/robotframework/blob/master/INSTALL.rst
.. _pip: http://pip-installer.org

Usage
-----

Robot Framework is executed from the command line using ``pybot``, ``jybot``
or ``ipybot`` scripts, depending is it run on Python, Jython or IronPython.
The basic usage is giving a path to a test case file or directory as
an argument with possible command line options before the path. Additionally
there is ``rebot`` tool for post-processing outputs.

Examples::

    pybot tests.txt
    jybot --variable HOST:example.com --outputdir results path/to/tests/
    rebot --name Example output1.xml output2.xml

Run ``pybot --help`` and ``rebot --help`` for more information about the command
line usage. If you are new to Robot Framework, you probably want to start
by looking examples at http://robotframework.org and studying demo projects
linked from there. For a complete reference manual see
`Robot Framewrk User Guide`_.

.. _Robot Framewrk User Guide: http://robotframework.org/robotframework/#user-guide

License
-------

Robot Framework code is provided under `Apache License 2.0`_
Documentation and other similar content use `Creative Commons
Attribution 3.0 Unported`_ license. Most libraries and tools in
the ecosystem are also open source, but they may use different
licenses.

.. _Apache License 2.0: http://apache.org/licenses/LICENSE-2.0
.. _Creative Commons Attribution 3.0 Unported: http://creativecommons.org/licenses/by/3.0
