=====================
Robot Framework 3.0.2
=====================

.. default-role:: code

Robot Framework 3.0.2 is the second minor release in the Robot Framework 3.0.x
series. The main motivation for this releases is fixing a performance regression
with evaluating expressions using some BuiltIn keywords occurring since RF 2.9
(`#2523`_), but there are also some other fixes and several nice enhancements.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
mailing list and possible bugs submitted to the `issue tracker
<https://github.com/robotframework/robotframework/issues>`__.

If you have `pip <http://pip-installer.org>`_ installed, just run
`pip install --upgrade robotframework` to install the latest
release or use `pip install robotframework==3.0.2` to install exactly
this version. Alternatively you can download the source distribution from
`PyPI <https://pypi.python.org/pypi/robotframework>`_ and install it manually.
For more details and other installation approaches, see the `installation
instructions <../../INSTALL.rst>`_.

Robot Framework 3.0.2 was released on Monday February 13, 2017.

.. contents::
   :depth: 2
   :local:

Most important fixes
====================

The biggest reason this release was created somewhat soon after
`RF 3.0.1 <rf-3.0.1.rst>`_ is fixing a performance regression in BuiltIn__
keywords like `Evaluate`, `Should Be True` and `Run Keyword If` that evaluate
expression in Python (`#2523`_). This regression originates already from RF 2.9,
but it is normally small enough not to be noticed. It can, however, slow
down execution considerably if the affected keywords are used a lot.

Most important enhancements
===========================

The most important new features in this release are the new `get_keyword_tags`
method in the dynamic and remote library interfaces (`#2538`_) and possibility
to disable validation of certain keywords in the dry-run mode (`#2528`_).
The Remote Protocol default port 8270 has also been `officially registered by
IANA`__ (`#2367`_).

__ http://robotframework.org/robotframework/latest/libraries/BuiltIn.html
__ http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml?search=8270

Acknowledgements
================

This release has been sponsored by the `Robot Framework Foundation`_.
Additionally Nokia Networks has been sponsoring the work related to
performance enhancements. Thanks also for `@cjnewman`__ for getting
the Remote Protocol default port registered.

__ https://github.com/cjnewman

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#2523`_
      - bug
      - critical
      - BuiltIn: Expression evaluation performance drop since RF 2.9
    * - `#2367`_
      - enhancement
      - high
      - Officially register Remote Protocol default port 8270
    * - `#2528`_
      - enhancement
      - high
      - Possibility to avoid executing keyword in dry-run based on special tag
    * - `#2538`_
      - enhancement
      - high
      - Add `get_keyword_tags` to dynamic library API and remote interface
    * - `#2532`_
      - bug
      - medium
      - XML: `Save XML` corrupts saved element when using lxml
    * - `#2299`_
      - enhancement
      - medium
      - Add some useful examples of prerun modifiers to the docs
    * - `#2420`_
      - enhancement
      - medium
      - Add `-A/--argumentfile` support in Testdoc
    * - `#2517`_
      - enhancement
      - medium
      - Dialogs: Resize selection list automatically to content with `Get Selection From User`
    * - `#2529`_
      - enhancement
      - medium
      - Document that pip does not recreate `robot.bat` and `rebot.bat` if installing same version multiple times
    * - `#2531`_
      - enhancement
      - medium
      - Functions starting with `_` but marked with `@keyword` decorator should become keywords
    * - `#2534`_
      - enhancement
      - medium
      - XML: Possibility to strip namespaces altogether
    * - `#2535`_
      - enhancement
      - medium
      - Support `--argumentfile` case-insensitively and document that shortening it does not work
    * - `#2428`_
      - bug
      - low
      - Ensure `args` passed to `start/end_keyword` listener methods are always strings
    * - `#2541`_
      - bug
      - low
      - Importing library with same name as Python built-in module fails with bad error message
    * - `#2306`_
      - enhancement
      - low
      - DateTime: Document that locale aware directives like `%b` don't work with Jython on non-English locales

Altogether 15 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A3.0.2>`__.

.. _User Guide: http://robotframework.org/robotframework/#user-guide
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _#2523: https://github.com/robotframework/robotframework/issues/2523
.. _#2367: https://github.com/robotframework/robotframework/issues/2367
.. _#2528: https://github.com/robotframework/robotframework/issues/2528
.. _#2538: https://github.com/robotframework/robotframework/issues/2538
.. _#2532: https://github.com/robotframework/robotframework/issues/2532
.. _#2299: https://github.com/robotframework/robotframework/issues/2299
.. _#2420: https://github.com/robotframework/robotframework/issues/2420
.. _#2517: https://github.com/robotframework/robotframework/issues/2517
.. _#2529: https://github.com/robotframework/robotframework/issues/2529
.. _#2531: https://github.com/robotframework/robotframework/issues/2531
.. _#2534: https://github.com/robotframework/robotframework/issues/2534
.. _#2535: https://github.com/robotframework/robotframework/issues/2535
.. _#2428: https://github.com/robotframework/robotframework/issues/2428
.. _#2541: https://github.com/robotframework/robotframework/issues/2541
.. _#2306: https://github.com/robotframework/robotframework/issues/2306
