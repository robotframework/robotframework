=====================
Robot Framework 3.0.3
=====================

.. default-role:: code

`Robot Framework`_ 3.0.3 is a new release containing mainly bug fixes but
also few nice enhancements. Questions and comments related to the release
can be sent to the `robotframework-users`_ mailing list or to
`Robot Framework Slack`_, and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==3.0.3

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.0.3 was released on Friday April 6, 2018.

.. _Robot Framework: http://robotframework.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.0.3
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst


.. contents::
   :depth: 2
   :local:

Most important fixes and enhancements
=====================================

- Using typing hints or keyword-only-arguments prevented using function as keyword (`#2627`_)
- `RuntimeWarning` printed on console when using `robot` command with Python 3.6 on Windows (`#2552`_)
- Content Security Policy (CSP) causes problems with report (`#2606`_)
- Terminal emulation in Telnet library is not compatible with latest `pyte` versions (`#2693`_)
- Use new logo as favicon in output files (`#2793`_)

Backwards incompatible changes
==============================

Supported version of pyte module used by Telnet library changed
---------------------------------------------------------------

The Telnet library has optional support for terminal emulation that utilizes
the `pyte <https://pyte.readthedocs.io/>`_ module. Due to changes in pyte 0.6,
earlier Telnet library versions were not compatible with it and pyte 0.5.2
was needed instead. This has now been fixed, but nowadays the Telnet library
only supports pyte 0.6 or newer. For more details see issue `#2693`_.

Keywords finding errors are not syntax errors
---------------------------------------------

Errors related to finding keywords are not be considered syntax errors
anymore (`#2792`_). In practice this means that keywords executing other
keywords, like `Wait Until Keyword Succeeds`, can catch these errors and
the test is not failed immediately. Although the change is
backwards-incompatible, it is not expected to cause problems in real usage.

The main reason this change was done in a minor release was to allow
teardowns to continue execution if keywords are not found. This was changed
in RF 3.0.1 and that change did cause real problems (`#2648`_).

Acknowledgements
================

Robot Framework 3.0.3 development has been sponsored by
`Robot Framework Foundation <http://robotframework.org/foundation/>`_.
Thanks also everyone submitting issues, testing preview releases, helping
others on support forums, and so on.

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#2627`_
      - bug
      - critical
      - Using typing hints or keyword-only-arguments prevents using function as keyword
    * - `#2552`_
      - bug
      - high
      - `RuntimeWarning` printed on console when using `robot` command with Python 3.6 on Windows
    * - `#2606`_
      - bug
      - high
      - Content Security Policy (CSP) causes problems with report
    * - `#2693`_
      - bug
      - high
      - Terminal emulation in Telnet library is not compatible with latest `pyte` versions
    * - `#2793`_
      - enhancement
      - high
      - Use new logo as favicon in output files
    * - `#1433`_
      - bug
      - medium
      - Importing `String` and `DateTime` fails on Windows and OSX if `PYTHONCASEOK` is set or installation directory shared between VM and host
    * - `#2548`_
      - bug
      - medium
      - `rebot --merge` doesn't work correctly if test messages contain HTML
    * - `#2599`_
      - bug
      - medium
      - Dry Run fails if library keywords use embedded arguments
    * - `#2648`_
      - bug
      - medium
      - Regression: Execution stops in teardown if keyword is not found
    * - `#2709`_
      - bug
      - medium
      - [ ERROR ] Unexpected error: IOError: [Errno 0] Error
    * - `#2732`_
      - bug
      - medium
      - Appending to test message using HTML doesn't work if old message is not HTML
    * - `#2739`_
      - bug
      - medium
      - Custom string subclasses not always handled correctly (e.g. `Convert To Integer`)
    * - `#2756`_
      - bug
      - medium
      - Zero length test library causes infinite recursion
    * - `#2763`_
      - bug
      - medium
      - Timeouts do not stop execution if they occur during execution of `log_message` listener method
    * - `#2779`_
      - bug
      - medium
      - `robot.libdoc` doesn't support specifying doc format although its docs say it does
    * - `#2785`_
      - bug
      - medium
      - Syntax errors (non-fatal) when installing with easy_install using Python 3
    * - `#2794`_
      - bug
      - medium
      - Process library keywords leave file descriptors open on Python 2
    * - `#2600`_
      - enhancement
      - medium
      - Dictionary variables should support attribute access with nested dictionaries
    * - `#2792`_
      - enhancement
      - medium
      - Errors related to finding keywords should not be considered syntax errors
    * - `#2760`_
      - bug
      - low
      - `Take Screenshot` keyword causes warning when using wxPython 4
    * - `#2656`_
      - enhancement
      - low
      - String 'NONE' should be considered `False` when used as Boolean argument
    * - `#2755`_
      - enhancement
      - low
      - Change Selenium2Library to SeleniumLibrary in user guide documentation. 

Altogether 22 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.0.3>`__.

.. _#2627: https://github.com/robotframework/robotframework/issues/2627
.. _#2552: https://github.com/robotframework/robotframework/issues/2552
.. _#2606: https://github.com/robotframework/robotframework/issues/2606
.. _#2693: https://github.com/robotframework/robotframework/issues/2693
.. _#2793: https://github.com/robotframework/robotframework/issues/2793
.. _#1433: https://github.com/robotframework/robotframework/issues/1433
.. _#2548: https://github.com/robotframework/robotframework/issues/2548
.. _#2599: https://github.com/robotframework/robotframework/issues/2599
.. _#2648: https://github.com/robotframework/robotframework/issues/2648
.. _#2709: https://github.com/robotframework/robotframework/issues/2709
.. _#2732: https://github.com/robotframework/robotframework/issues/2732
.. _#2739: https://github.com/robotframework/robotframework/issues/2739
.. _#2756: https://github.com/robotframework/robotframework/issues/2756
.. _#2763: https://github.com/robotframework/robotframework/issues/2763
.. _#2779: https://github.com/robotframework/robotframework/issues/2779
.. _#2785: https://github.com/robotframework/robotframework/issues/2785
.. _#2794: https://github.com/robotframework/robotframework/issues/2794
.. _#2600: https://github.com/robotframework/robotframework/issues/2600
.. _#2792: https://github.com/robotframework/robotframework/issues/2792
.. _#2760: https://github.com/robotframework/robotframework/issues/2760
.. _#2656: https://github.com/robotframework/robotframework/issues/2656
.. _#2755: https://github.com/robotframework/robotframework/issues/2755
