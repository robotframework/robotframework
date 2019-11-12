===========================
Robot Framework 3.1 alpha 1
===========================


.. default-role:: code


`Robot Framework`_ 3.1 is a new major release with terminology configuration
to support Robotic Process Automation (RPA) and several other nice planned
features. RF 3.1 alpha 1 is its first preview release which mainly contains
initial RPA support as well as enhancements to installation.

All issues targeted for Robot Framework v3.1 can be found
from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==3.1a1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.1a1 was released on Thursday June 7, 2018.

.. _Robot Framework: http://robotframework.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Terminology configuration to support Robotic Process Automation (RPA)
---------------------------------------------------------------------

`Robotic Process Automation (RPA)`__ means automating business processes that
typically have been designed for humans and thus involve lot of GUIs. As
an automation tool Robot Framework has always supported this kind of usage
as well, but it has been a bit awkward to create test cases and to get
test reports and test logs as a result.

RF 3.1 is taking first steps to really make Robot Framework a valid RPA
tool by allowing creating *tasks* instead of tests and changing terminology
in reports and logs when tasks are executed. There are two ways to activate
the RPA mode:

1. Use the new `*** Tasks ***` (or `*** Task ***`) header in test data files
   instead of the normal `*** Test Cases ***` header. This is useful when it
   is important that data contains tasks, not tests. It is an error to run
   multiple files together so that some have tasks and others have tests.

2. Use the new command line option `--rpa`. This is convenient when executing
   data that needs to be compatible with earlier Robot Framework versions
   and when using editors that do not support the new `*** Tasks ***` header.
   Also Rebot supports the `--rpa` option, so it is possible to use older
   Robot Framework versions for execution and only create reports and logs
   using the `--rpa` option.

Regardless how the RPA mode is enabled, the generated reports and logs use
term "task", not "test".

As a convenience, a new command line option `--task` has been added as an
alias for the existing `--test` option.

__ https://en.wikipedia.org/wiki/Robotic_process_automation


Installation enhancements
-------------------------

There are various enhancements and other changes related to installation:

- The `robot` and `rebot` start-up scripts are nowadays `*.exe` files on
  Windows. They used to be `*.bat` files which caused all kinds of bigger
  and smaller issues. (`#2415`_ , alpha 1)

- Robot Framework is now distributed as a `wheel <http://pythonwheels.com>`_
  distribution making installation faster. (`#1734`_, alpha 1)

- Source distribution format has been changed from tar.gz to zip. (`#2830`_,
  alpha 1)

Backwards incompatible changes
==============================

- Python 2.6 and 3.3 are not supported anymore. (`#2276`_, alpha 1)

- Old start-up scripts `pybot`, `jybot`, `ipybot`, `jyrebot` and `ipyrebot`
  have been removed in favor of the generic `robot` and `rebot` scripts.
  (`#2818`_, alpha 1)

- Underscores are not be replaced with spaces in values given from the
  command line. For example, `--doc Underscores_are_preserved` will change
  the top-level suite documentation to `Underscores_are_preserved`. The fix
  is escaping or quoting spaces like `--doc "We got spaces"`. (`#2399`_, alpha 1)

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#2415`_
      - enhancement
      - critical
      - Use .exe wrappers instead of .bat under Windows
      - alpha 1
    * - `#2788`_
      - enhancement
      - critical
      - Terminology configuration to support usage in generic automation
      - alpha 1
    * - `#1734`_
      - enhancement
      - high
      - Provide `wheel` distribution
      - alpha 1
    * - `#2276`_
      - enhancement
      - high
      - Remove support for Python 2.6 and 3.3
      - alpha 1
    * - `#2818`_
      - enhancement
      - high
      - Remove `pybot`, `jybot`, `ipybot`, `jyrebot` and `ipyrebot` start-up scripts
      - alpha 1
    * - `#2399`_
      - bug
      - medium
      - Underscores should not be replaced with spaces in values given from command line
      - alpha 1
    * - `#2750`_
      - bug
      - medium
      - `PYTHONIOENCODING` is not honored with Python 2
      - alpha 1
    * - `#2817`_
      - bug
      - medium
      - `pip install -I` corrupts `robot.bat` if Robot Framework is already installed
      - alpha 1
    * - `#2829`_
      - bug
      - medium
      - Operating system encoding detection problems on Windows with Python 3.6
      - alpha 1
    * - `#2830`_
      - enhancement
      - medium
      - Change source distribution format from `tar.gz` to `zip`
      - alpha 1
    * - `#2834`_
      - bug
      - low
      - Problems with glob patterns on IronPython 2.7.8
      - alpha 1

Altogether 11 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1>`__.

.. _#2415: https://github.com/robotframework/robotframework/issues/2415
.. _#2788: https://github.com/robotframework/robotframework/issues/2788
.. _#1734: https://github.com/robotframework/robotframework/issues/1734
.. _#2276: https://github.com/robotframework/robotframework/issues/2276
.. _#2818: https://github.com/robotframework/robotframework/issues/2818
.. _#2399: https://github.com/robotframework/robotframework/issues/2399
.. _#2750: https://github.com/robotframework/robotframework/issues/2750
.. _#2817: https://github.com/robotframework/robotframework/issues/2817
.. _#2829: https://github.com/robotframework/robotframework/issues/2829
.. _#2830: https://github.com/robotframework/robotframework/issues/2830
.. _#2834: https://github.com/robotframework/robotframework/issues/2834
