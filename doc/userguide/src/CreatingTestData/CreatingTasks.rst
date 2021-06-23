.. _rpa:

Creating tasks
==============

In addition to test automation, Robot Framework can be used for other
automation purposes, including `robotic process automation`__ (RPA).
It has always been possible, but Robot Framework 3.1 added official
support for automating *tasks*, not only tests. For most parts creating
tasks works the same way as `creating tests`_ and the only real difference
is in terminology. Tasks can also be organized into suites__ exactly like
test cases.

__ https://en.wikipedia.org/wiki/Robotic_process_automation
__ `Creating test suites`_

.. contents::
   :depth: 2
   :local:

Task syntax
-----------

Tasks are created based on the available keywords exactly like test cases,
and the task syntax is in general identical to the `test case syntax`_.
The main difference is that tasks are created in Task sections
instead of Test Case sections:

.. sourcecode:: robotframework

   *** Tasks ***
   Process invoice
       Read information from PDF
       Validate information
       Submit information to backend system
       Validate information is visible in web UI

It is an error to have both tests and tasks in same file.

Task related settings
---------------------

Settings that can be used in the task section are exactly the same as in
the `test case section`__. In the `setting section`__ it is possible to use
:setting:`Task Setup`, :setting:`Task Teardown`, :setting:`Task Template`
and :setting:`Task Timeout` instead of their :setting:`Test` variants.

__ `Settings in the Test Case section`_
__ `Test case related settings in the Setting section`_
