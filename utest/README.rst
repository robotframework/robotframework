Robot Framework unit tests
==========================

Introduction
------------

Robot Framework's unit tests are implemented using Python's `unittest
<https://docs.python.org/library/unittest.html>`__ module, and they
all are in subdirectories of this directory. These tests are executed
automatically when all acceptance tests are executed, and how to run
unit tests manually is explained below.

Most of the Robot Framework's features are tested with acceptance tests
using the framework itself. Some of those tests would normally be
better implemented as unit tests, but we want to push the framework to
its limits (and eat our own dog food). A consequence to this is that
some features are not unit tested at all.

Running unit tests
------------------

All unit tests can be run with script ``run.py``. To get more
information run ``python run.py --help``.

Unit test files should always start with prefix ``test_``. This is the
mechanism the unit tests are found by the ``run.py`` script.

To run only certain unit tests you need to set the Robot Framework's ``src``
folder to ``PYTHONPATH`` and run the test like ``python path/test_xxx.py``.
There are also some unit tests that need some other modules i.e. libraries
used also in acceptance tests. The full list of paths needed to run all
the unit tests can be found from the beginning of the ``run.py`` file.
Often it is just easier to run all the unit tests.

Preconditions
-------------

Depending on the platform, unit tests may need some external modules to be
installed. Needed modules are is listed in the provided `<requirements.txt>`__
file and the easiest way to install them is running::

    pip install -r utest/requirements.txt

License and copyright
---------------------

All content in the ``utest`` directory is under the following copyright::

    Copyright 2008-2015 Nokia Networks
    Copyright 2016-     Robot Framework Foundation

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
