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

The `robot.api`__ package exposes the public Robot Framework API.

Following APIs are available:

  * :py:func:`~robot.result.resultbuilder.ExecutionResult` for reading
    execution results from a xml file.

  * :py:class:`~robot.parsing.model.TestCaseFile`,
    :py:class:`~robot.parsing.model.TestDataDirectory`,and
    :py:class:`~robot.parsing.model.ResourceFile` for parsing data files to
    objects. In addition, a convenience function
    :py:func:`~robot.parsing.model.TestData` creates either
    :py:class:`~robot.parsing.model.TestCaseFile` or
    :py:class:`~robot.parsing.model.TestDataDirectory` based on input.

  * :py:func:`~robot.running.model.TestSuite` for creating a
    test suite that can be executed programmatically.

__ robot.api.html

All of the above members can be imported like

.. code-block:: python

    from robot.api import <name>


All packages
============

.. toctree::
    :maxdepth: 1

    robot
    robot.api
    robot.common
    robot.conf
    robot.htmldata
    robot.libdocpkg
    robot.libraries
    robot.model
    robot.output
    robot.parsing
    robot.reporting
    robot.result
    robot.running
    robot.utils
    robot.variables
    robot.writer


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
