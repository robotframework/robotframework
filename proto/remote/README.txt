Robot Framework Remote Library
==============================

Introduction
------------

This directory contains a prototype implementation of Robot Framework
Remote Library. The idea of the library is having a thin Python proxy
library that communicates using XML-RPC protocol with the actual
library implementation. The main benefits of this idea are:

- It is possible to have the library on another machine than Robot Framework.
- It is possible to implement the library using any language that has
  XML-RPC modules (Ruby, Perl, ...).

The plan is to eventually have the remote library proxy as one of the
Robot Framework's standard libraries. We also plan to have remote
server implementations using different languages under `tools`. We'll
start from the Python remote server and next on the list (and already
under development) is Ruby server.


What we currently have
----------------------

1. Proxy library that is in the same machine and interpreter than
   Robot Framework itself. This library is in `Remote.py` file and it
   is more or less ready.

2. Python remote server implementation in `python/robotremoteserver.py`
   file. This part is also quite ready, and the biggest missing
   "feature" is documentation. There's also an example test library in
   `python/examplelibrary.py` that uses the Python remote server.

3. Ruby remote server in `ruby/robotremoteserver.rb` file. Basic
   features are implemented, but there's still some work to do. The
   biggest problem is that the test execution hangs when running many
   remote keywords against the Ruby remote server. The limit when
   tests hang seems to depend on how powerful the machine running
   tests is. The problem may be due to our code not releasing some
   resources like it should, or there can be a bug in Ruby's XML-RPC,
   HTTP or socket modules. This server is used by an example library
   in `ruby/examplelibrary.rb` file.

4. Automated tests and a test runner. See `running tests`_ below for
   more information.


Todo
----

1.0 version
~~~~~~~~~~~

At this point we can move `Remote.py` under `src/robot/libraries` and
everything else under `tools/remote`.  Must have the proxy library and
Python remote server ready.

1. Lots of documentation (this README is a start)
2. Additional tests for
   - big integers and floats
   - bigger integers than allowed by xmlrpc
   - long strings
   - something else?
3. Add copyrights

As a bonus we should fix `issue 133`__ to get rid of warnings about
duplicate tests, when executing tests for remote library.

__ http://code.google.com/p/robotframework/issues/detail?id=133


1.1 version
~~~~~~~~~~~

1. Investigate the Ruby hanging problem
2. Finalize Ruby remote server
3. Investigate the possibility that remote libraries extend the remote 
   server directly.
4. Investigate having one server "hosting" multiple libraries.


Running tests
-------------

The general syntax for running tests is::

   run_tests.py <language> [options] [datasources]

This runs tests using a custom test runner. The step it does are:

1. Start the remote server based on the selected language
2. Execute tests using `pybot --include <language>`
3. Stop the remote server
4. Use `statuschecker.py` tool to check test statuses

Run just `run_tests.py` and see Python and Ruby examples below
to get more information.

It is also possible to start the remote server and execute tests manually.


Python
~~~~~~ 

When running tests on Python, all tests should pass. 

Run all tests::

   run_tests.py python

Run only certain test suite::

   run_tests.py python test/basic_communication.html 

Use additional options::

   run_tests.py python --test LogLevels test/logging.html 


Ruby
~~~~ 

Ruby version of the remote server does not yet have all the features
so some tests fail. A bigger problem is that tests hang when they
execute a bigger number of remote keywords.

Run all tests (this probably hangs)::

   run_tests.py ruby

Run other basic tests than the one executing 100 keywords (this should
pass)::

   run_tests.py ruby --exclude long test/basic_communication.html 

Runthe problematic `Use Remote Keyword Multiple Times` test with a
custom number of iterations (small numbers normally pass)::

   run_tests.py ruby --test UseRemoteKeywordMultipleTimes
           --variable COUNT:10 test/basic_communication.html
