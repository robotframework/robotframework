Robot Framework Remote Servers
==============================

Introduction
------------

This directory contains remote server implementations that can be used
with the Remote library. The main source for information related to the
Remote library and remote servers is the User Guide. 

Implemented Remote Servers
--------------------------

There are currently remote server implemenations for Python and Ruby in
`robotremoteserver.py` and `robotremoteserver.rb` files, respectively.
The plan is to implement at least Java and Perl versions in the future.

Examples Using Remote Servers
-----------------------------

Examples on how to use the remote servers can be found from `example`
directory. These example servers can be started with following
commands, assuming that the module search path is set so
that the respective remote server modules can be imported::

   python example/examplelibrary.py
   ruby example/examplelibrary.rb

These examples will start the remote server so that it provided
keywords implemented in the example module. After the remote server is
started, an example test case file can be executed normally::

   pybot example/example.html


Testing Remote Servers
----------------------

Tests for the remote servers are inside `test` directory. Acceptance tests
can be executed using `tests/run.py` script and running the script without
arguments provided more information. Notice that tests are not included in 
source distributions.
