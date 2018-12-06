.. _executing tasks:

Task execution
==============

Robot Framework can be used also for other automation purposes than test
automation, and starting from Robot Framework 3.1 it is possible to
explicitly create__ and execute tasks. For most parts task execution
and test execution work the same way, and this section explains the
differences.

__ `Creating tasks`_

.. contents::
   :depth: 2
   :local:

Generic automation mode
-----------------------

When Robot Framework is used execute a file and it notices that the file
has tasks, not tests, it automatically sets itself into the generic automation
mode. This mode does not change the actual execution at all, but when
logs and reports are created, they use term *task*, not *test*. They have,
for example, headers like `Task Log` and `Task Statistics` instead of
`Test Log` and `Test Statistics`.

The generic automation mode can also be enabled by using the :option:`--rpa`
option. In that case the executed files can have either tests or tasks.
Alternatively :option:`--norpa` can be used to force the test automation
mode even if executed files contain tasks. If neither of these options are
used, it is an error to execute multiple files so that some have tests and
others have tasks.

The execution mode is stored in the generated `output file`_ and read by
Rebot_ if outputs are post-processed. The mode can also `be set when
using Rebot`__ if necessary.

__ `Controlling execution mode`_

Task related command line options
---------------------------------

All normal command line options can be used when executing tasks. If there
is a need to `select only certain tasks for execution`__, :option:`--task`
can be used instead of :option:`--test`. Additionally the aforementioned
:option:`--rpa` can be used to control the execution mode.

__ `Selecting test cases`_
