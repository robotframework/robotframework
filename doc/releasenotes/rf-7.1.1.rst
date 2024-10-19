=====================
Robot Framework 7.1.1
=====================

.. default-role:: code

`Robot Framework`_ 7.1.1 is the first and also the only planned bug fix release
in the Robot Framework 7.1.x series. It fixes all reported regressions as well as
some issues affecting also earlier versions.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.1.1

to install exactly this version. Alternatively, you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.1.1 was released on Saturday October 19, 2024.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Acknowledgements
================

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its over 60 member organizations. If your organization is using Robot Framework
and benefiting from it, consider joining the foundation to support its
development as well.

Big thanks to the Foundation and to everyone who has submitted bug reports, debugged
problems, or otherwise helped with Robot Framework development.

| `Pekka Klärck <https://github.com/pekkaklarck>`_
| Robot Framework lead developer

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#5205`_
      - bug
      - high
      - Execution fails at the end when using `--output NONE` and console hyperlinks are enabled
    * - `#5224`_
      - bug
      - high
      - Test is not failed if listener sets keyword status to fail and leaves message empty
    * - `#5212`_
      - bug
      - medium
      - Execution fails if standard streams are not available
    * - `#5237`_
      - bug
      - medium
      - Keyword timeout is not effective in teardown if keyword uses `Wait Until Keyword Succeeds`
    * - `#5206`_
      - enhancement
      - medium
      - Document that `output_file` listener method is called with `None` when using `--output NONE`

Altogether 5 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.1.1>`__.

.. _#5205: https://github.com/robotframework/robotframework/issues/5205
.. _#5224: https://github.com/robotframework/robotframework/issues/5224
.. _#5212: https://github.com/robotframework/robotframework/issues/5212
.. _#5237: https://github.com/robotframework/robotframework/issues/5237
.. _#5206: https://github.com/robotframework/robotframework/issues/5206
