Unit Tests
==========

Introduction
------------

Robot Framework's unit tests are implemented using Python's `testunit`
module (a.k.a. PyUnit), and they all are in subdirectories of this
directory. These tests are executed automatically when all acceptance
tests are executed, and how to run unit tests manually is explained below.

Most of the Robot Framework's features are tested with acceptance test
using the framework itself. Some of those tests would normally be
better implemented as unit tests, but we want to push the framework to
its limits (and eat our own dog food). As a consequence to this is
that some features are not unit tested at all and in general there are
not that many unit tests.

License and Copyright
---------------------

All the content in the 'utest' folder is under following copyright:

  Copyright 2008-2009 Nokia Siemens Networks Oyj

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

Running Unit Tests
------------------

All unit tests can be run with script 'run_utests.py'. To get more information 
run 'python run_utests.py --help'. Python and Jython interpreter should be used 
to verify interoperability with both supported interpreters. Unit test files 
should always start with prefix 'test_'. This is the mechanism the unit tests 
are found by the 'run_utests.py' script. 

To run only certain unit tests you need to set the Robot Framework's 'src'
folder to PYTHONPATH and run the test like 'python path/test_xxx.py'. There are
are also some unit tests that need some other modules i.e. libraries used also
in acceptance tests. The full list of paths needed to run all the unit tests
can be found from the beginning of the 'run_utests.py' file. Usually it is just
easier to run all the unit tests.
