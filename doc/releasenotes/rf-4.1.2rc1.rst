=========================================
Robot Framework 4.1.2 release candidate 1
=========================================

.. default-role:: code

`Robot Framework`_ 4.1.2 is the last planned bug fix release in the RF 4.1.x
series. It is also the last planned release to support Python 2 that itself
`has not been supported since January 2020`__. Unfortunately this also means
the end of our Jython__ and IronPython__ support at least until the get
Python 3 compatible versions released.

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

   pip install robotframework==4.1.2rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.1.2 rc 1 was released on Monday October 4, 2021.
The final release is targeted for Monday October 11, 2021. If you are still
using Python 2, Jython or IronPython, we highly recommend you to test this
release candidate in your own environment before that. Reported problems
will still be fixed before the release, even if that would delay the release,
but there are no plans for further RF 4.1.x releases after that.

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

Java integration fixes
----------------------

RF 4.1.2 being the last planned release to support Jython and Java, it is good that
these two high priority issues were fixed in it:

- Java versions with version number not in format `<major>.<minor>.<patch>`
  (e.g. `16.0.1`) did not work at all. OpenJDK releases use just `<major>` as
  their initial version number adding `<minor>` and `<patch>` parts only in
  possible bug fix releases. As the result, using Robot Framework with Jython
  on OpenJDK 17 was not possible at all. (`#4100`_)

- Extending the standalone JAR distribution was not possible. (`#3780`_)


Lines starting with `|` not followed by space caused crash
----------------------------------------------------------

For example, lines like `||` and `|whatever` crashed Robot Framework's parser
for good preventing execution altogether. (`#4082`_)

Acknowledgements
================

Robot Framework 4.1.2 development has been sponsored by the `Robot Framework Foundation`_
and its `close to 50 member organizations <https://robotframework.org/foundation/#members>`_.
Big thanks for the foundation for its continued support! If your organization is using
Robot Framework and finds it useful, consider joining the foundation to make make
sure it is maintained and developed further also in the future.

Robot Framework 4.1.2 was a pretty small release, but there was one great pull
request by the wider open source community. Thanks `Michel Hidalgo
<https://github.com/hidmic>`__ for enhancing error handling with
reStructuredText files. (`#4086`_)

Big thanks also to everyone else who has submitted bug reports, helped debugging
problems, or otherwise helped with this release.

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
    * - `#4102`_
      - enhancement
      - medium
      - Process: Make it possible to configure standard input stream

Altogether 6 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1.2>`__.

.. _#4100: https://github.com/robotframework/robotframework/issues/4100
.. _#4082: https://github.com/robotframework/robotframework/issues/4082
.. _#3780: https://github.com/robotframework/robotframework/issues/3780
.. _#4065: https://github.com/robotframework/robotframework/issues/4065
.. _#4086: https://github.com/robotframework/robotframework/issues/4086
.. _#4102: https://github.com/robotframework/robotframework/issues/4102
