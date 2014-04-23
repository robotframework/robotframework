Remote library interface
------------------------

The remote library interface provides means for having test libraries
on different machines than where Robot Framework itself is running,
and also for implementing libraries using other languages than the
natively supported Python and Java. For a test library user remote
libraries look pretty much the same as any other test library, and
developing test libraries using the remote library interface is also
very close to creating `normal test libraries`__.

__ `Creating test libraries`_

.. contents::
   :depth: 2
   :local:

Introduction
~~~~~~~~~~~~

There are two main reasons for using the remote library API:

* It is possible to have actual libraries on different machines than
  where Robot Framework is running. This allows interesting
  possibilities for distributed testing.

* Test libraries can be implemented using any language that supports
  `XML-RPC`_ protocol. Robot Framework 2.1 contains generic `remote
  servers`_ for Python/Jython and Ruby, and the community has implemented
  generic servers for other languages like Java, .NET and Perl.

The remote library interface is provided by the Remote library that is
one of the `standard libraries`_ starting from Robot Framework
2.1. This library does not have any keywords of its own, but it works
as a proxy between the core framework and keywords implemented
elsewhere. The Remote library interacts with actual library
implementations through `remote servers`_, and the Remote library and
servers communicate using a simple `remote protocol`_ on top of an
XML-RPC channel.  The high level architecture of all this is
illustrated in the picture below:

.. figure:: src/ExtendingRobotFramework/remote.png

   Robot Framework architecture with Remote library

.. note:: The remote client uses Python's standard xmlrpclib__ module. It does
          not support custom XML-RPC extensions implemented by some XML-RPC
          servers.

__ http://docs.python.org/2/library/xmlrpclib.html

Taking Remote library into use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Importing Remote library
''''''''''''''''''''''''

The Remote library needs to know the address of the remote server but
otherwise importing it and using keywords that it provides is no
different to how other libraries are used. If you need to use the Remote
library multiple times in a test suite, or just want to give it a more
descriptive name, you can import it using the `WITH NAME syntax`_.

.. table:: Importing Remote library
   :class: example

   =========  ===========  ========================  =========  =========
    Setting      Value               Value             Value      Value
   =========  ===========  ========================  =========  =========
   Library    Remote       \http://127.0.0.1:8270    WITH NAME  Example1
   Library    Remote       \http://example.com:7777  WITH NAME  Example2
   Library    Remote       \http://10.0.0.2/example  WITH NAME  Example3
   =========  ===========  ========================  =========  =========

The URL used by the first example above is also the default address
that the Remote library uses if no address is given. Similarly port
:code:`8270` is the port that remote servers are expected to use by default.
(82 and 70 are the ASCII codes of letters `R` and `F`, respectively.)

.. note:: When connecting to the local machine, it is recommended to use
          address :code:`127.0.0.1` instead of :code:`localhost`. This avoids
          address resolution that can be extremely slow `at least on Windows`__.
          Prior to Robot Framework 2.8.4 the Remote library itself used the
          potentially slow :code:`localhost` by default.

.. note:: Depending on the remote server, the trailing slash after the server
          address may or may not be significant. For example, using
          :code:`http://127.0.0.1:8270` is not always the same as using
          :code:`http://127.0.0.1:8270/`. If there is a difference, remote
          servers themselves should document which format to use.

__ http://stackoverflow.com/questions/14504450/pythons-xmlrpc-extremely-slow-one-second-per-call

Starting and stopping remote servers
''''''''''''''''''''''''''''''''''''

Before the Remote library can be imported, the remote server providing
the actual keywords must be started.  If the server is started before
launching the test execution, it is possible to use the normal
:opt:`Library` setting like in the above example. Alternatively other
keywords, for example from OperatingSystem or SSH libraries, can start
the server up, but then you may need to use `Import Library keyword`__
because the library is not available when the test execution starts.

How a remote server can be stopped depends on how it is
implemented. Following methods work with the servers distributed with
Robot Framework:

* Regardless of the library used, remote servers provide :name:`Stop
  Remote Server` keyword that can be used from the test data.
* Remote servers have :code:`stop_remote_server` method in their
  XML-RPC interface.
* :code:`Ctrl-C` stops the server if it is running on a terminal
  window. Unfortunately this does not work with all servers on all
  operating systems.
* The server process can be terminated using tools provided by the
  operating system (e.g. :prog:`kill`).

.. note:: The server may be configured so that users cannot stop it with
          :name:`Stop Remote Server` keyword or :code:`stop_remote_server`
          method.

__ `Using Import Library keyword`_

Supported argument and return value types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because the XML-RPC protocol does not support all possible object
types, the values transferred between the Remote library and remote
servers must be converted to compatible types. This applies to the
keyword arguments the Remote library passes to remote servers and to
the return values servers give back to the Remote library.

Both the Remote library and the Python remote server handle Python values
according to the following rules. Other remote servers should behave similarly.

* Strings, numbers and Boolean values are passed without modifications.
* Python :code:`None` is converted to an empty string.
* All lists, tuples, and other iterable objects (except strings and
  dictionaries) are passed as lists so that their contents are converted
  recursively.
* Dictionaries and other mappings are passed as dicts so that their keys are
  converted to strings and values converted to supported types recursively.
* Strings containing bytes in the ASCII range that cannot be represented in
  XML (e.g. the null byte) are sent as `Binary objects`__ that internally use
  XML-RPC base64 data type. Received Binary objects are automatically converted
  to byte strings.
* Other types are converted to strings.

.. note:: Prior to Robot Framework 2.8.3, only lists, tuples, and dictionaries
          were handled according to the above rules. General iterables
          and mappings were not supported.

          Binary support is new in Robot Framework 2.8.4.

__ http://docs.python.org/2/library/xmlrpclib.html#binary-objects

Using remote servers
~~~~~~~~~~~~~~~~~~~~

Robot Framework 2.1 includes remote server implementations written
both in Python and Ruby. These servers, as well as the example
libraries shown below and an example test case file, are
included in source distributions under :path:`tools/remoteserver`
directory and available also at
http://code.google.com/p/robotframework/wiki/RemoteLibrary.

The provided servers are designed so that it is easy to create test
libraries using them. With both of the servers the basic procedure is
as follows:

* Create a test library module or class similarly as a normal test
  library using the `static library API`_. With the Python server it
  is also possible to use the `hybrid library API`_.
* Import the remote server class and create an instance of it giving
  the library instance or module to it as an argument. The listening
  address and port, possibly got from the command line, can be given
  as optional arguments.

Both these steps can be done in the same module as illustrated by the
examples below. Executing these modules as scripts from the command
line will start the remote server so that it serves the keywords
implemented in the library.

Python remote library example
'''''''''''''''''''''''''''''

This example demonstrates how to use the Python version of the
remote server. The example library implements keywords :name:`Count
Items In Directory` and :name:`Strings Should Be Equal`.

.. sourcecode:: python

   ../../tools/remoteserver/example/examplelibrary.py

Ruby remote library example
'''''''''''''''''''''''''''

This example uses the Ruby remote server and provides exactly same
keywords as the previous Python example:

.. sourcecode:: ruby

   ../../tools/remoteserver/example/examplelibrary.rb

Remote protocol
~~~~~~~~~~~~~~~

This section explains the protocol that is used between the Remote
library and remote servers. This information is mainly targeted for
people who want to create new remote servers. The provided Python and
Ruby servers can also be used as examples.

The remote protocol is implemented on top of `XML-RPC`_, which is a
simple remote procedure call protocol using XML over HTTP. Most
mainstream languages (Python, Java, C, Ruby, Perl, Javascript, PHP,
...) have a support for XML-RPC either built-in or as an extension.

Required methods
''''''''''''''''

A remote server is an XML-RPC server that must have the same methods
in its public interface as the `dynamic library API`_ has. Only
:code:`get_keyword_names` and :code:`run_keyword` are actually
required, but :code:`get_keyword_arguments` and
:code:`get_keyword_documentation` are also recommended. Notice that
using camelCase format in method names is not possible currently. How
the actual keywords are implemented is not relevant for the Remote
library.  A remote server can either act as a wrapper for real test
libraries, like the provided Python and Ruby servers do, or it can
implement keywords itself.

Remote servers should additionally have :code:`stop_remote_server`
method in their public interface to ease stopping them. They should
also automatically expose this method as :name:`Stop Remote Server`
keyword to allow using it in the test data regardless of the test
library. Allowing users to stop the server is not always desirable,
and servers may support disabling this functionality somehow.
The method, and also the exposed keyword, should return :code:`True`
or :code:`False` depending was stopping allowed or not. That makes it
possible for external tools to know did stopping the server succeed.

The provided Python remote server can be used as a reference
implementation.

Getting remote keyword names and other information
''''''''''''''''''''''''''''''''''''''''''''''''''

The Remote library gets a list of keywords that the remote server
provides using :code:`get_keyword_names` method. This method must
return the keyword names as a list of strings.

Remote servers can, and should, also implement
:code:`get_keyword_arguments` and :code:`get_keyword_documentation`
methods to provide more information about the keywords. Both of these
keywords get the name of the keyword as an argument. Arguments must be
returned as a list of strings in the `same format as with dynamic
libraries`__, and documentation must be returned `as a string`__.

Starting from Robot Framework 2.6.2, remote servers can also provide
`general library documentation`__ to be used when generating
documenation with `libdoc`_ tool.

__ `Getting keyword arguments`_
__ `Getting keyword documentation`_
__ `Getting general library documentation`_

Executing remote keywords
'''''''''''''''''''''''''

When the Remote library wants the server to execute some keyword, it
calls remote server's :code:`run_keyword` method and passes it the
keyword name, a list of arguments, and possibly a dictionary of
`free keyword arguments`__. Base types can be used as
arguments directly, but more complex types are `converted to supported
types`__.

The server must return results of the execution in a result dictionary
(or map, depending on terminology) containing items explained in the
following table. Notice that only the :code:`status` entry is mandatory,
others can be omitted if they are not applicable.

.. table:: Entries in the remote result dictionary
   :class: tabular

   +------------+-------------------------------------------------------------+
   |     Name   |                         Explanation                         |
   +============+=============================================================+
   | status     | Mandatory execution status. Either PASS or FAIL.            |
   +------------+-------------------------------------------------------------+
   | output     | Possible output to write into the log file. Must be given   |
   |            | as a single string but can contain multiple messages and    |
   |            | different `log levels`__ in format :msg:`*INFO* First       |
   |            | message\\n*HTML* <b>2nd</b>\\n*WARN* Another message`. It   |
   |            | is also possible to embed timestamps_ to the log messages   |
   |            | like :msg:`*INFO:1308435758660* Message with timestamp`.    |
   +------------+-------------------------------------------------------------+
   | return     | Possible return value. Must be one of the `supported        |
   |            | types`__.                                                   |
   +------------+-------------------------------------------------------------+
   | error      | Possible error message. Used only when the execution fails. |
   +------------+-------------------------------------------------------------+
   | traceback  | Possible stack trace to `write into the log file`__ using   |
   |            | DEBUG level when the execution fails.                       |
   +------------+-------------------------------------------------------------+
   | continuable| When set to :code:`True`, or any value considered           |
   |            | :code:`True` in Python, the occurred failure is considered  |
   |            | continuable__. New in Robot Framework 2.8.4.                |
   +------------+-------------------------------------------------------------+
   | fatal      | Like :code:`continuable`, but denotes that the occurred     |
   |            | failure is fatal__. Also new in Robot Framework 2.8.4.      |
   +------------+-------------------------------------------------------------+

__ `Different argument syntaxes`_
__ `Supported argument and return value types`_
__ `Logging information`_
__ `Supported argument and return value types`_
__ `Reporting keyword status`_
__ `Continue on failure`_
__ `Stopping test execution gracefully`_

Different argument syntaxes
'''''''''''''''''''''''''''

The Remote library is a `dynamic library`_, and in general it handles
different argument syntaxes `according to the same rules`__ as any other
dynamic library.
This includes mandatory arguments, default values, varargs, as well
as `named argument syntax`__.

Also free keyword arguments (:code:`**kwargs`) works mostly the `same way
as with other dynamic libraries`__. First of all, the
:code:`get_keyword_arguments` must return an argument specification that
contains :code:`**kwargs` exactly like with any other dynamic library.
The main difference is that
remote servers' :code:`run_keyword` method must have optional third argument
that gets the kwargs specified by the user. The third argument must be optional
because, for backwards-compatibility reasons, the Remote library passes kwargs
to the :code:`run_keyword` method only when they have been used in the test data.

In practice :code:`run_keyword` should look something like the following
Python and Java examples, depending on how the language handles optional
arguments.

.. sourcecode:: python

    def run_keyword(name, args, kwargs=None):
        # ...


.. sourcecode:: java

    public Map run_keyword(String name, List args) {
        // ...
    }

    public Map run_keyword(String name, List args, Map kwargs) {
        // ...
    }

.. note:: Remote library supports :code:`**kwargs` starting from
          Robot Framework 2.8.3.

__ `Getting keyword arguments`_
__ `Named argument syntax with dynamic libraries`_
__ `Free keyword arguments with dynamic libraries`_
