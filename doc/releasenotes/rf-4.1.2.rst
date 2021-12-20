=====================
Robot Framework 4.1.2
=====================

.. default-role:: code

`Robot Framework`_ 4.1.2 contains a considerable enhancement to memory usage
along with some bug fixes. It is the last planned release in the whole Robot
Framework 4.x series and also the last planned release to support Python 2
that itself `has not been supported since January 2020`__. Unfortunately this
also means the end of our Jython__ and IronPython__ support, at least until
they get Python 3 compatible versions released.

__ https://www.python.org/doc/sunset-python-2/
__ http://jython.org
__ http://ironpython.net

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==4.1.2

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.1.2 was released on Friday October 15, 2021.
It contained a small regression related to parsing `reStructuredText
<https://en.wikipedia.org/wiki/ReStructuredText>`_ files that was fixed in
`Robot Framework 4.1.3 <rf-4.1.3.rst>`_ released on Wednesday December 15, 2021.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1.2
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Reduce memory usage
-------------------

Robot Framework 4.1.2 uses considerably less memory than earlier versions
especially when processing large output.xml files. Exact numbers vary depending
on the executed tests or tasks, but the reduction compared to Robot Framework
4.1.1 can be over 30%. Memory consumption had actually increased in Robot
Framework 4.0, but these fixes drop it below Robot Framework 3.2 levels. (`#4114`_)

Memory usage was profiled using the `Fil <https://pythonspeed.com/fil/>`_ tool.
It made it easy to see that memory usage had increased and, more importantly,
where memory was spent. The latter allowed making small changes in few places
to drop memory usage considerably.

Java integration fixes
----------------------

Robot Framework 4.1.2 being the last planned release to support Jython and Java,
it is good that these two high priority issues were fixed:

- Java versions with version number not in format `<major>.<minor>.<patch>`
  (e.g. `16.0.1`) did not work at all. OpenJDK releases use just `<major>`
  (e.g. `17`) as their initial version number and apparently add `<minor>` and
  `<patch>` parts only in possible bug fix releases. As the result, using
  Robot Framework on, for example, OpenJDK 17 was not possible. (`#4100`_)

- Extending the standalone JAR distribution was not possible. (`#3780`_)

Fixes to parser crashes
-----------------------

Parser had two bugs resulting to crashes preventing the whole execution. Such
crashes are always severe, but luckily both cases required somewhat special
syntax. Crashes occurred in these cases:

- If a line started with a pipe character (`|`) and was not followed by a space
  or a newline character (e.g. `||` or `|whatever`). (`#4082`_)
- If a variable assignment missed the closing `}` and had `=` at the end
  (e.g. `${oops =`). (`#4118`_)

Backwards incompatible changes
==============================

Rebot's merge functionality ignored suite setups and teardowns earlier. As
the result final outputs contained old, possibly failing, setups and teardowns.
This problem was fixed and now suites always have setups and teardowns
from the last merged run. This is better behavior, but it is possible that
someone is dependent on the old behavior. That possibility was considered so
unlikely, however, that we decided to make the change in a patch release
(RF 4.1.2) instead of waiting for a major release (RF 5.0). (`#4120`_)

Acknowledgements
================

Robot Framework 4.1.2 development has been sponsored by the `Robot Framework Foundation`_
and its `close to 50 member organizations <https://robotframework.org/foundation/#members>`_.
Big thanks for the foundation for its continued support! If your organization is using
Robot Framework and finds it useful, consider joining the foundation to make
sure it is maintained and developed further also in the future.

Robot Framework 4.1.2 was a pretty small release, but it had two great pull
requests by the wider open source community:

- `Michel Hidalgo <https://github.com/hidmic>`__ enhanced error handling with
  reStructuredText files. (`#4086`_)
- `Daniel Biehl  <https://github.com/d-biehl>`__ fixed handling broken variable
  assignment like `${oops =` (`#4118`_)

Big thanks to contributors and also to everyone else who has submitted bug
reports, helped debugging problems, or otherwise helped with this release.

| `Pekka Klärck <https://github.com/pekkaklarck>`__
| Robot Framework Creator

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#4100`_
      - bug
      - critical
      - Java versions with version number not in format `<major>.<minor>.<patch>` do not work (e.g. OpenJDK 17)
    * - `#4082`_
      - bug
      - high
      - Lines starting with `|` not followed by space cause crash
    * - `#4118`_
      - bug
      - high
      - Broken variable assignment with like `${oops =` crashes parsing
    * - `#4114`_
      - enhancement
      - high
      - Reduce memory usage
    * - `#3780`_
      - bug
      - medium
      - Extending JAR distribution fails
    * - `#4065`_
      - bug
      - medium
      - Process: Started processes can hang due to how stdin is configured
    * - `#4086`_
      - bug
      - medium
      - All irrelevant errors are not silenced when parsing reStructuredText data
    * - `#4112`_
      - bug
      - medium
      - Incompatible output.xml created if listener runs keyword in `end_keyword` inside FOR loop
    * - `#4120`_
      - bug
      - medium
      - `rebot --merge` doesn't merge suite setups or teardowns
    * - `#4102`_
      - enhancement
      - medium
      - Process: Make it possible to configure standard input stream
    * - `#4116`_
      - bug
      - low
      - `Should Be Equal` ignores custom error messages when comparing multiline strings

Altogether 11 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1.2>`__.

.. _#4100: https://github.com/robotframework/robotframework/issues/4100
.. _#4082: https://github.com/robotframework/robotframework/issues/4082
.. _#4118: https://github.com/robotframework/robotframework/issues/4118
.. _#4114: https://github.com/robotframework/robotframework/issues/4114
.. _#3780: https://github.com/robotframework/robotframework/issues/3780
.. _#4065: https://github.com/robotframework/robotframework/issues/4065
.. _#4086: https://github.com/robotframework/robotframework/issues/4086
.. _#4112: https://github.com/robotframework/robotframework/issues/4112
.. _#4120: https://github.com/robotframework/robotframework/issues/4120
.. _#4102: https://github.com/robotframework/robotframework/issues/4102
.. _#4116: https://github.com/robotframework/robotframework/issues/4116
