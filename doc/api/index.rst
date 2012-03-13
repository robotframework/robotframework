=================================
Robot Framework API documentation
=================================


This document describes the public API of Robot Framework. Installation,
basic usage and wealth of other topics are covered in the `user guide`__.

__ http://code.google.com/p/robotframework/wiki/UserGuide

.. toctree::
    :maxdepth: 2


Entry points
============

Command line entry points are implemented as Python modules and they also
have programmatic APIs. Following entry points exist:

  * :py:mod:`robot.run` entry point for executing tests.
  * :py:mod:`robot.rebot` entry point for post-processing outputs.
  * :py:mod:`robot.libdoc` entry point for the `libdoc`__ tool.
  * :py:mod:`robot.testdoc` entry point for the `testdoc`__ tool.
  * :py:mod:`robot.tidy` entry point for the `tidy`__ tool.

__ http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool
__ http://code.google.com/p/robotframework/wiki/TestDataDocumentationTool
__ http://code.google.com/p/robotframework/wiki/TestDataTidyingTool


Public API
==========

.. automodule:: robot.api


All packages
============

Packages and modules not listed in the chapters above are considered private,
and included here only for reference.

.. toctree::
    :maxdepth: 1
    :glob:

    autodoc/*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
