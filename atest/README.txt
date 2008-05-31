Acceptance Tests
================


Introduction
------------

Acceptance tests for Robot Framework are naturally created using Robot 
Framework itself. This folder contains all those acceptance tests and other
test data they need. 


License and Copyright
---------------------

All the content in the atest folder is under following copyright::

    Copyright 2008 Nokia Siemens Networks Oyj

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


Directory contents
------------------

run_atests.py
    A script for running acceptance tests. See below for further
   instructions.

robot/
    Contains actual acceptance test cases. 

resources/
    Resources needed by acceptance tests in 'robot' folder.

testdata/
    Contains test data used by acceptance tests. This test data consists
    mainly of test cases that are run by actual acceptance tests in 'robot'
    folder. 
  
testresources/
    Contains resources needed by test cases in 'testdata' folder. Some
    of these resources are also used by unit tests.
  
results/
    The place for test execution results like reports, logs and outputs. 
    This directory is generated when acceptance tests are executed. It
    is in 'svn:ignore' and can be safely deleted.


Running Acceptance Tests
------------------------

Robot Framework's acceptance tests are run using 'run_atests.py'. Its 
usage is displayed with '--help' and also shown below::

    Usage: run_atests.py interpreter [options] datasource(s)

    Data sources are paths to directories or files under 'robot' folder.

    Available options are the same that can be used with Robot Framework.
    See its help (e.g. 'pybot --help') for more information.

    The specified interpreter is used by acceptance tests under 'robot' to
    run test cases under 'testdata'. It can be simply 'python' or 'jython'
    (if they are in PATH) or a path to a selected interpreter (e.g.
    '/usr/bin/python23'). Note that this script itself must always be
    executed with Python.

    Examples:
    $ atest/run_atests.py python --splitoutputs 2 atest/robot
    $ atest/run_atests.py /usr/bin/jython22 atest/robot/core/variables.html


To run all the acceptance tests, execute the 'atest/robot' folder entirely.
A sub test suite can be executed simply by running the folder or file 
containing it. On modern machines running all acceptance tests ought to
take less than ten minutes with Python, but with Jython the execution time 
is considerably longer. This is due to Jython being somewhat slower than
Python in general, but the main reason is that the JVM is started by
acceptance dozens of times and it always takes few seconds.

When acceptance tests are run, both Python and Jython interpreter should be
used to verify interoperability with both supported interpreters. Tests
can (and should) also be run using different Python and Jython versions and
on different operating systems. 

The results of the test execution are written to 'results' folder. The 
directory contains output, log and report files that are named based on
the startup script used to run the test cases (e.g. 'jybot-log.html'). 
The directory also contains time-stampped folders for other test outputs.


Test Data
---------

The test data is divided to two, test data part ('testdata' folder') and
running part ('robot' folder). Test data side contains test cases for
different features. Running side contains the actual acceptance test cases
that run the test cases on the test data side and verify their results.

The basic mechanism to verify that test cases in the test data side
are executed as expected, is setting the expected status and possible
error message in the documentation of the test cases. Normally test
cases are expected to pass, but having 'FAIL' in the documentation
changes the expectation. Text after 'FAIL' should contain the exact
error message or, when the text starts with 'REGEXP:', a regular
expression matching the error. All other details can be tested also,
but that logic is in the running side.

These acceptance tests are in general *not* good examples of
well-written test cases. This is mainly due to us learning how to
write good test cases with Robot Framework while developing it, and so
far there has not been time for refactoring them. With better tools
refactorig is getting easier and hopefully we can do something for
these tests in the future. The first step would be reorganizing the
structure of 'robot' and 'testdata' folders. Their current structure
follows Robot Framework's old internal module structure and it is far
from ideal nowadays.
