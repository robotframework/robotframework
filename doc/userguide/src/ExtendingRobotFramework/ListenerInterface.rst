Listener interface
==================

Robot Framework has a listener interface that can be used to receive
notifications about test execution. Example usages include
external test monitors, sending a mail message when a test fails, and
communicating with other systems. Listener API version 3 also makes
it possible to modify tests and results during the test execution.

Listeners are classes or modules with certain special methods, and they
can be implemented both with Python and Java. Listeners that monitor
the whole test execution must be taken into use from the command line.
In addition to that, `test libraries can register listeners`__ that receive
notifications while that library is active.

__ `Libraries as listeners`_

.. contents::
   :depth: 2
   :local:

Taking listeners into use
-------------------------

Listeners are taken into use from the command line with the :option:`--listener`
option so that the name of the listener is given to it as an argument. The
listener name is got from the name of the class or module implementing the
listener, similarly as `library name`_ is got from the class or module
implementing the library. The specified listeners must be in the same `module
search path`_ where test libraries are searched from when they are imported.
Other option is to give an absolute or a relative path to the listener file
`similarly as with test libraries`__. It is possible to take multiple listeners
into use by using this option several times::

   robot --listener MyListener tests.robot
   robot --listener com.company.package.Listener tests.robot
   robot --listener path/to/MyListener.py tests.robot
   robot --listener module.Listener --listener AnotherListener tests.robot

It is also possible to give arguments to listener classes from the command
line. Arguments are specified after the listener name (or path) using a colon
(`:`) as a separator. If a listener is given as an absolute Windows path,
the colon after the drive letter is not considered a separator.
Additionally it is possible to use a semicolon (`;`) as an
alternative argument separator. This is useful if listener arguments
themselves contain colons, but requires surrounding the whole value with
quotes on UNIX-like operating systems::

   robot --listener listener.py:arg1:arg2 tests.robot
   robot --listener "listener.py;arg:with:colons" tests.robot
   robot --listener c:\path\listener.py;d:\first\arg;e:\second\arg tests.robot

In addition to passing arguments one-by-one as positional arguments, it is
possible to pass them using the `named argument syntax`_ exactly when using
keywords::

   robot --listener listener.py:name=value tests.robot
   robot --listener "listener.py;name=value:with:colons;another=value" tests.robot

Listener arguments are automatically converted using `same rules as with
keywords`__ based on `type hints`__ and `default values`__. For example,
this listener

.. sourcecode:: python

    class Listener(object):

        def __init__(self, port: int, log=True):
            self.port = post
            self.log = log

could be used like ::

    robot --listener Listener:8270:false

and the first argument would be converted to an integer based on the type hint
and the second to a Boolean based on the default value.

.. note:: Both named argument syntax and argument conversion are new in
          Robot Framework 4.0.

__ `Using physical path to library`_
__ `Supported conversions`_
__ `Specifying argument types using function annotations`_
__ `Implicit argument types based on default values`_

Listener interface versions
---------------------------

There are two supported listener interface versions. A listener must
have an attribute `ROBOT_LISTENER_API_VERSION` with value 2 or 3, either as
a string or as an integer, depending on which API version it uses.

The main difference between listener versions 2 and 3 is that the former only
gets information about the execution but cannot directly affect it. The latter
interface gets data and result objects Robot Framework itself uses and is thus
able to alter execution and change results. See `listener examples`_ for more
information about what listeners can do.

Another difference between versions 2 and 3 is that the former supports
both Python and Java but the latter supports only Python.

Listener interface methods
--------------------------

Robot Framework creates instances of listener classes when the test execution
starts and uses listeners implemented as modules directly. During the test
execution different listener methods are called when test suites, test cases
and keywords start and end. Additional methods are called when a library or
a resource or variable file is imported, when output files are ready, and
finally when the whole test execution ends. A listener is not required to
implement any official interface, and it only needs to have the methods it
actually needs.

Listener versions 2 and 3 have mostly the same methods, but the arguments
they accept are different. These methods and their arguments are explained
in the following sections. All methods that have an underscore in their name
have also *camelCase* alternative. For example, `start_suite` method can
be used also with name `startSuite`.

Listener version 2
~~~~~~~~~~~~~~~~~~

Listener methods in the API version 2 are listed in the following table.
All methods related to test execution progress have the same signature
`method(name, attributes)`, where `attributes` is a dictionary containing
details of the event. Listener methods are free to do whatever they want
to do with the information they receive, but they cannot directly change
it. If that is needed, `listener version 3`_ can be used instead.

.. table:: Methods in the listener API 2
   :class: tabular

   +------------------+------------------+----------------------------------------------------------------+
   |    Method        |    Arguments     |                          Documentation                         |
   +==================+==================+================================================================+
   | start_suite      | name, attributes | Called when a test suite starts.                               |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `id`: Suite id. `s1` for the top level suite, `s1-s1`        |
   |                  |                  |   for its first child suite, `s1-s2` for the second            |
   |                  |                  |   child, and so on.                                            |
   |                  |                  | * `longname`: Suite name including parent suites.              |
   |                  |                  | * `doc`: Suite documentation.                                  |
   |                  |                  | * `metadata`: `Free test suite metadata`_ as a dictionary/map. |
   |                  |                  | * `source`: An absolute path of the file/directory the suite   |
   |                  |                  |   was created from.                                            |
   |                  |                  | * `suites`: Names of the direct child suites this suite has    |
   |                  |                  |   as a list.                                                   |
   |                  |                  | * `tests`: Names of the tests this suite has as a list.        |
   |                  |                  |   Does not include tests of the possible child suites.         |
   |                  |                  | * `totaltests`: The total number of tests in this suite.       |
   |                  |                  |   and all its sub-suites as an integer.                        |
   |                  |                  | * `starttime`: Suite execution start time.                     |
   +------------------+------------------+----------------------------------------------------------------+
   | end_suite        | name, attributes | Called when a test suite ends.                                 |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `id`: Same as in `start_suite`.                              |
   |                  |                  | * `longname`: Same as in `start_suite`.                        |
   |                  |                  | * `doc`: Same as in `start_suite`.                             |
   |                  |                  | * `metadata`: Same as in `start_suite`.                        |
   |                  |                  | * `source`: Same as in `start_suite`.                          |
   |                  |                  | * `starttime`: Same as in `start_suite`.                       |
   |                  |                  | * `endtime`: Suite execution end time.                         |
   |                  |                  | * `elapsedtime`: Total execution time in milliseconds as       |
   |                  |                  |   an integer                                                   |
   |                  |                  | * `status`: Suite status as string `PASS`, `FAIL` or `SKIP`.   |
   |                  |                  | * `statistics`: Suite statistics (number of passed             |
   |                  |                  |   and failed tests in the suite) as a string.                  |
   |                  |                  | * `message`: Error message if suite setup or teardown          |
   |                  |                  |   has failed, empty otherwise.                                 |
   +------------------+------------------+----------------------------------------------------------------+
   | start_test       | name, attributes | Called when a test case starts.                                |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `id`: Test id in format like `s1-s2-t2`, where               |
   |                  |                  |   the beginning is the parent suite id and the last part       |
   |                  |                  |   shows test index in that suite.                              |
   |                  |                  | * `longname`: Test name including parent suites.               |
   |                  |                  | * `originalname`: Test name with possible variables            |
   |                  |                  |   unresolved. New in RF 3.2.                                   |
   |                  |                  | * `doc`: Test documentation.                                   |
   |                  |                  | * `tags`: Test tags as a list of strings.                      |
   |                  |                  | * `template`: The name of the template used for the test.      |
   |                  |                  |   An empty string if the test not templated.                   |
   |                  |                  | * `source`: An absolute path of the test case source file.     |
   |                  |                  |   New in RF 4.0.                                               |
   |                  |                  | * `lineno`: Line number where the test starts in the source    |
   |                  |                  |   file. New in RF 3.2.                                         |
   |                  |                  | * `starttime`: Test execution execution start time.            |
   +------------------+------------------+----------------------------------------------------------------+
   | end_test         | name, attributes | Called when a test case ends.                                  |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `id`: Same as in `start_test`.                               |
   |                  |                  | * `longname`: Same as in `start_test`.                         |
   |                  |                  | * `originalname`: Same as in `start_test`.                     |
   |                  |                  | * `doc`: Same as in `start_test`.                              |
   |                  |                  | * `tags`: Same as in `start_test`.                             |
   |                  |                  | * `template`: Same as in `start_test`.                         |
   |                  |                  | * `source`: Same as in `start_test`.                           |
   |                  |                  | * `lineno`: Same as in `start_test`.                           |
   |                  |                  | * `starttime`: Same as in `start_test`.                        |
   |                  |                  | * `endtime`: Test execution execution end time.                |
   |                  |                  | * `elapsedtime`: Total execution time in milliseconds as       |
   |                  |                  |   an integer                                                   |
   |                  |                  | * `status`: Test status as string `PASS`, `FAIL` or `SKIP`.    |
   |                  |                  | * `message`: Status message. Normally an error                 |
   |                  |                  |   message or an empty string.                                  |
   +------------------+------------------+----------------------------------------------------------------+
   | start_keyword    | name, attributes | Called when a keyword starts.                                  |
   |                  |                  |                                                                |
   |                  |                  | `name` is the full keyword name containing                     |
   |                  |                  | possible library or resource name as a prefix.                 |
   |                  |                  | For example, `MyLibrary.Example Keyword`.                      |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `type`: String specifying keyword type. Possible values are: |
   |                  |                  |   `KEYWORD`, `SETUP`, `TEARDOWN`, `FOR`, `FOR ITERATION`, `IF`,|
   |                  |                  |   `ELSE IF` and `ELSE`. **NOTE:** Prior to RF 4.0 values were: |
   |                  |                  |   `Keyword`, `Setup`, `Teardown`, `For` and `For Item`.        |
   |                  |                  | * `kwname`: Name of the keyword without library or             |
   |                  |                  |   resource prefix. String representation of parameters with    |
   |                  |                  |   FOR and IF/ELSE structures.                                  |
   |                  |                  | * `libname`: Name of the library or resource file the keyword  |
   |                  |                  |   belongs to. An empty string when the keyword is in a test    |
   |                  |                  |   case file and with FOR and IF/ELSE structures.               |
   |                  |                  | * `doc`: Keyword documentation.                                |
   |                  |                  | * `args`: Keyword's arguments as a list of strings.            |
   |                  |                  | * `assign`: A list of variable names that keyword's            |
   |                  |                  |   return value is assigned to.                                 |
   |                  |                  | * `tags`: `Keyword tags`_ as a list of strings.                |
   |                  |                  | * `source`: An absolute path of the file where the keyword was |
   |                  |                  |   used. New in RF 4.0.                                         |
   |                  |                  | * `lineno`: Line where the keyword was used. New in RF 4.0.    |
   |                  |                  | * `status`: Initial keyword status. `NOT RUN` if keyword is    |
   |                  |                  |   not executed (e.g. due to an earlier failure), `NOT SET`     |
   |                  |                  |   otherwise. New in RF 4.0.                                    |
   |                  |                  | * `starttime`: Keyword execution start time.                   |
   +------------------+------------------+----------------------------------------------------------------+
   | end_keyword      | name, attributes | Called when a keyword ends.                                    |
   |                  |                  |                                                                |
   |                  |                  | `name` is the full keyword name containing                     |
   |                  |                  | possible library or resource name as a prefix.                 |
   |                  |                  | For example, `MyLibrary.Example Keyword`.                      |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `type`: Same as with `start_keyword`.                        |
   |                  |                  | * `kwname`: Same as with `start_keyword`.                      |
   |                  |                  | * `libname`: Same as with `start_keyword`.                     |
   |                  |                  | * `doc`: Same as with `start_keyword`.                         |
   |                  |                  | * `args`: Same as with `start_keyword`.                        |
   |                  |                  | * `assign`: Same as with `start_keyword`.                      |
   |                  |                  | * `tags`: Same as with `start_keyword`.                        |
   |                  |                  | * `source`: Same as with `start_keyword`.                      |
   |                  |                  | * `lineno`: Same as with `start_keyword`.                      |
   |                  |                  | * `starttime`: Same as with `start_keyword`.                   |
   |                  |                  | * `endtime`: Keyword execution end time.                       |
   |                  |                  | * `elapsedtime`: Total execution time in milliseconds as       |
   |                  |                  |   an integer                                                   |
   |                  |                  | * `status`: Keyword status as string `PASS`, `FAIL`, `SKIP`    |
   |                  |                  |   or `NOT RUN`. `SKIP` and `NOT RUN` are new in RF 4.0.        |
   +------------------+------------------+----------------------------------------------------------------+
   | log_message      | message          | Called when an executed keyword writes a log message.          |
   |                  |                  |                                                                |
   |                  |                  | `message` is a dictionary with the following contents:         |
   |                  |                  |                                                                |
   |                  |                  | * `message`: The content of the message.                       |
   |                  |                  | * `level`: `Log level`_ used in logging the message.           |
   |                  |                  | * `timestamp`: Message creation time in format                 |
   |                  |                  |   `YYYY-MM-DD hh:mm:ss.mil`.                                   |
   |                  |                  | * `html`: String `yes` or `no` denoting whether the message    |
   |                  |                  |   should be interpreted as HTML or not.                        |
   |                  |                  |                                                                |
   |                  |                  | Not called if the message level is below the current           |
   |                  |                  | `threshold level <Log levels_>`__.                             |
   +------------------+------------------+----------------------------------------------------------------+
   | message          | message          | Called when the framework itself writes a syslog_ message.     |
   |                  |                  |                                                                |
   |                  |                  | `message` is a dictionary with the same contents as with       |
   |                  |                  | `log_message` method.                                          |
   +------------------+------------------+----------------------------------------------------------------+
   | library_import   | name, attributes | Called when a library has been imported.                       |
   |                  |                  |                                                                |
   |                  |                  | `name` is the name of the imported library. If the library     |
   |                  |                  | has been imported using the `WITH NAME syntax`_, `name` is     |
   |                  |                  | the specified alias.                                           |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `args`: Arguments passed to the library as a list.           |
   |                  |                  | * `originalname`: The original library name when using the     |
   |                  |                  |   WITH NAME syntax, otherwise same as `name`.                  |
   |                  |                  | * `source`: An absolute path to the library source. `None`     |
   |                  |                  |   with libraries implemented with Java or if getting the       |
   |                  |                  |   source of the library failed for some reason.                |
   |                  |                  | * `importer`: An absolute path to the file importing the       |
   |                  |                  |   library. `None` when BuiltIn_ is imported well as when       |
   |                  |                  |   using the :name:`Import Library` keyword.                    |
   +------------------+------------------+----------------------------------------------------------------+
   | resource_import  | name, attributes | Called when a resource file has been imported.                 |
   |                  |                  |                                                                |
   |                  |                  | `name` is the name of the imported resource file without       |
   |                  |                  | the file extension.                                            |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `source`: An absolute path to the imported resource file.    |
   |                  |                  | * `importer`: An absolute path to the file importing the       |
   |                  |                  |   resource file. `None` when using the :name:`Import Resource` |
   |                  |                  |   keyword.                                                     |
   +------------------+------------------+----------------------------------------------------------------+
   | variables_import | name, attributes | Called when a variable file has been imported.                 |
   |                  |                  |                                                                |
   |                  |                  | `name` is the name of the imported variable file with          |
   |                  |                  | the file extension.                                            |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `args`: Arguments passed to the variable file as a list.     |
   |                  |                  | * `source`: An absolute path to the imported variable file.    |
   |                  |                  | * `importer`: An absolute path to the file importing the       |
   |                  |                  |   resource file. `None` when using the :name:`Import           |
   |                  |                  |   Variables` keyword.                                          |
   +------------------+------------------+----------------------------------------------------------------+
   | output_file      | path             | Called when writing to an `output file`_ is ready.             |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | log_file         | path             | Called when writing to a `log file`_ is ready.                 |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | report_file      | path             | Called when writing to a `report file`_ is ready.              |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | xunit_file       | path             | Called when writing to an `xunit file`_ is ready.              |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | debug_file       | path             | Called when writing to a `debug file`_ is ready.               |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | close            |                  | Called when the whole test execution ends.                     |
   |                  |                  |                                                                |
   |                  |                  | With `library listeners`_ called when the library goes out     |
   |                  |                  | of scope.                                                      |
   +------------------+------------------+----------------------------------------------------------------+

The available methods and their arguments are also shown in a formal Java
interface specification below. Contents of the `java.util.Map attributes` are
as in the table above.  It should be remembered that a listener *does not* need
to implement any explicit interface or have all these methods.

.. sourcecode:: java

   public interface RobotListenerInterface {
       public static final int ROBOT_LISTENER_API_VERSION = 2;
       void startSuite(String name, java.util.Map attributes);
       void endSuite(String name, java.util.Map attributes);
       void startTest(String name, java.util.Map attributes);
       void endTest(String name, java.util.Map attributes);
       void startKeyword(String name, java.util.Map attributes);
       void endKeyword(String name, java.util.Map attributes);
       void logMessage(java.util.Map message);
       void message(java.util.Map message);
       void outputFile(String path);
       void logFile(String path);
       void reportFile(String path);
       void debugFile(String path);
       void close();
   }

Listener version 3
~~~~~~~~~~~~~~~~~~

Listener version 3 has mostly the same methods as `listener version 2`_
but arguments of the methods related to test execution are different.
This API gets actual running and result model objects used by Robot
Framework itself, and listeners can both directly query information
they need and also change the model objects on the fly.

Listener version 3 does not yet have all methods that the version 2 has. The
main reason is that `suitable model objects are not available internally`__.
The `close` method and methods related to output files are called exactly
same way in both versions.

__ https://github.com/robotframework/robotframework/issues/1208#issuecomment-164910769

.. table:: Methods in the listener API 3
   :class: tabular

   +------------------+------------------+----------------------------------------------------------------+
   |    Method        |    Arguments     |                          Documentation                         |
   +==================+==================+================================================================+
   | start_suite      | data, result     | Called when a test suite starts.                               |
   |                  |                  |                                                                |
   |                  |                  | `data` and `result` are model objects representing             |
   |                  |                  | the `executed test suite <running.TestSuite_>`__ and `its      |
   |                  |                  | execution results <result.TestSuite_>`__, respectively.        |
   +------------------+------------------+----------------------------------------------------------------+
   | end_suite        | data, result     | Called when a test suite ends.                                 |
   |                  |                  |                                                                |
   |                  |                  | Same arguments as with `start_suite`.                          |
   +------------------+------------------+----------------------------------------------------------------+
   | start_test       | data, result     | Called when a test case starts.                                |
   |                  |                  |                                                                |
   |                  |                  | `data` and `result` are model objects representing             |
   |                  |                  | the `executed test case <running.TestCase_>`__ and `its        |
   |                  |                  | execution results <result.TestCase_>`__, respectively.         |
   +------------------+------------------+----------------------------------------------------------------+
   | end_test         | data, result     | Called when a test case ends.                                  |
   |                  |                  |                                                                |
   |                  |                  | Same arguments as with `start_test`.                           |
   +------------------+------------------+----------------------------------------------------------------+
   | start_keyword    | N/A              | Not currently implemented.                                     |
   +------------------+------------------+----------------------------------------------------------------+
   | end_keyword      | N/A              | Not currently implemented.                                     |
   +------------------+------------------+----------------------------------------------------------------+
   | log_message      | message          | Called when an executed keyword writes a log message.          |
   |                  |                  | `message` is a model object representing the `logged           |
   |                  |                  | message <result.Message_>`__.                                  |
   |                  |                  |                                                                |
   |                  |                  | This method is not called if the message has level below       |
   |                  |                  | the current `threshold level <Log levels_>`__.                 |
   +------------------+------------------+----------------------------------------------------------------+
   | message          | message          | Called when the framework itself writes a syslog_ message.     |
   |                  |                  |                                                                |
   |                  |                  | `message` is same object as with `log_message`.                |
   +------------------+------------------+----------------------------------------------------------------+
   | library_import   | N/A              | Not currently implemented.                                     |
   +------------------+------------------+----------------------------------------------------------------+
   | resource_import  | N/A              | Not currently implemented.                                     |
   +------------------+------------------+----------------------------------------------------------------+
   | variables_import | N/A              | Not currently implemented.                                     |
   +------------------+------------------+----------------------------------------------------------------+
   | output_file      | path             | Called when writing to an `output file`_ is ready.             |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | log_file         | path             | Called when writing to a `log file`_ is ready.                 |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | report_file      | path             | Called when writing to a `report file`_ is ready.              |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | xunit_file       | path             | Called when writing to an `xunit file`_ is ready.              |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | debug_file       | path             | Called when writing to a `debug file`_ is ready.               |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file.                        |
   +------------------+------------------+----------------------------------------------------------------+
   | close            |                  | Called when the whole test execution ends.                     |
   |                  |                  |                                                                |
   |                  |                  | With `library listeners`_ called when the library goes out     |
   |                  |                  | of scope.                                                      |
   +------------------+------------------+----------------------------------------------------------------+

Listeners logging
-----------------

Robot Framework offers a `programmatic logging APIs`_ that listeners can
utilize. There are some limitations, however, and how different listener
methods can log messages is explained in the table below.

.. table:: How listener methods can log
   :class: tabular

   +----------------------+---------------------------------------------------+
   |         Methods      |                   Explanation                     |
   +======================+===================================================+
   | start_keyword,       | Messages are logged to the normal `log file`_     |
   | end_keyword,         | under the executed keyword.                       |
   | log_message          |                                                   |
   +----------------------+---------------------------------------------------+
   | start_suite,         | Messages are logged to the syslog_. Warnings are  |
   | end_suite,           | shown also in the `execution errors`_ section of  |
   | start_test, end_test | the normal log file.                              |
   +----------------------+---------------------------------------------------+
   | message              | Messages are normally logged to the syslog. If    |
   |                      | this method is used while a keyword is executing, |
   |                      | messages are logged to the normal log file.       |
   +----------------------+---------------------------------------------------+
   | Other methods        | Messages are only logged to the syslog.           |
   +----------------------+---------------------------------------------------+

.. note:: To avoid recursion, messages logged by listeners are not sent to
          listener methods `log_message` and `message`.

Listener examples
-----------------

This section contains examples using the listener interface. There are
first examples that just receive information from Robot Framework and then
examples that modify executed tests and created results.

Getting information
~~~~~~~~~~~~~~~~~~~

The first example is implemented as Python module and uses the `listener
version 2`_.

.. sourcecode:: python

   """Listener that stops execution if a test fails."""

   ROBOT_LISTENER_API_VERSION = 2

   def end_test(name, attrs):
       if attrs['status'] == 'FAIL':
           print('Test "%s" failed: %s' % (name, attrs['message']))
           raw_input('Press enter to continue.')

If the above example would be saved to, for example, :file:`PauseExecution.py`
file, it could be used from the command line like this::

   robot --listener path/to/PauseExecution.py tests.robot

The same example could also be implemented also using the newer
`listener version 3`_ and used exactly the same way from the command line.

.. sourcecode:: python

   """Listener that stops execution if a test fails."""

   ROBOT_LISTENER_API_VERSION = 3

   def end_test(data, result):
       if not result.passed:
           print('Test "%s" failed: %s' % (result.name, result.message))
           raw_input('Press enter to continue.')

The next example, which still uses Python, is slightly more complicated. It
writes all the information it gets into a text file in a temporary directory
without much formatting. The filename may be given from the command line, but
also has a default value. Note that in real usage, the `debug file`_
functionality available through the command line option :option:`--debugfile` is
probably more useful than this example.

.. sourcecode:: python

   import os.path
   import tempfile


   class PythonListener:
       ROBOT_LISTENER_API_VERSION = 2

       def __init__(self, filename='listen.txt'):
           outpath = os.path.join(tempfile.gettempdir(), filename)
           self.outfile = open(outpath, 'w')

       def start_suite(self, name, attrs):
           self.outfile.write("%s '%s'\n" % (name, attrs['doc']))

       def start_test(self, name, attrs):
           tags = ' '.join(attrs['tags'])
           self.outfile.write("- %s '%s' [ %s ] :: " % (name, attrs['doc'], tags))

       def end_test(self, name, attrs):
           if attrs['status'] == 'PASS':
               self.outfile.write('PASS\n')
           else:
               self.outfile.write('FAIL: %s\n' % attrs['message'])

       def end_suite(self, name, attrs):
            self.outfile.write('%s\n%s\n' % (attrs['status'], attrs['message']))

       def close(self):
            self.outfile.close()

The following example implements the same functionality as the previous one,
but uses Java instead of Python.

.. sourcecode:: java

   import java.io.*;
   import java.util.Map;
   import java.util.List;


   public class JavaListener {
       public static final int ROBOT_LISTENER_API_VERSION = 2;
       public static final String DEFAULT_FILENAME = "listen_java.txt";
       private BufferedWriter outfile = null;

       public JavaListener() throws IOException {
           this(DEFAULT_FILENAME);
       }

       public JavaListener(String filename) throws IOException {
           String tmpdir = System.getProperty("java.io.tmpdir");
           String sep = System.getProperty("file.separator");
           String outpath = tmpdir + sep + filename;
           outfile = new BufferedWriter(new FileWriter(outpath));
       }

       public void startSuite(String name, Map attrs) throws IOException {
           outfile.write(name + " '" + attrs.get("doc") + "'\n");
       }

       public void startTest(String name, Map attrs) throws IOException {
           outfile.write("- " + name + " '" + attrs.get("doc") + "' [ ");
           List tags = (List)attrs.get("tags");
           for (int i=0; i < tags.size(); i++) {
              outfile.write(tags.get(i) + " ");
           }
           outfile.write(" ] :: ");
       }

       public void endTest(String name, Map attrs) throws IOException {
           String status = attrs.get("status").toString();
           if (status.equals("PASS")) {
               outfile.write("PASS\n");
           }
           else {
               outfile.write("FAIL: " + attrs.get("message") + "\n");
           }
       }

       public void endSuite(String name, Map attrs) throws IOException {
           outfile.write(attrs.get("status") + "\n" + attrs.get("message") + "\n");
       }

       public void close() throws IOException {
           outfile.close();
       }
   }

Modifying execution and results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These examples illustrate how to modify the executed tests and suites
as well as the execution results. All these examples require using
the `listener version 3`_.

Modifying executed suites and tests
'''''''''''''''''''''''''''''''''''

Changing what is executed requires modifying the model object containing
the executed `test suite <running.TestSuite_>`__ or `test case
<running.TestCase_>`__ objects passed as the first argument to `start_suite`
and `start_test` methods. This is illustrated by the example below that
adds a new test to each executed test suite and a new keyword to each test.

.. sourcecode:: python

   ROBOT_LISTENER_API_VERSION = 3

   def start_suite(suite, result):
       suite.tests.create(name='New test')

   def start_test(test, result):
       test.keywords.create(name='Log', args=['Keyword added by listener!'])

Trying to modify execution in `end_suite` or `end_test` methods does not work,
simply because that suite or test has already been executed. Trying to modify
the name, documentation or other similar metadata of the current suite or
test in `start_suite` or `start_test` method does not work either, because
the corresponding result object has already been created. Only changes to
child tests or keywords actually have an effect.

This API is very similar to the `pre-run modifier`_ API that can be used
to modify suites and tests before the whole test execution starts. The main
benefit of using the listener API is that modifications can be done
dynamically based on execution results or otherwise. This allows, for example,
interesting possibilities for model based testing.

Although the listener interface is not built on top of Robot Framework's
internal `visitor interface`_ similarly as the pre-run modifier API,
listeners can still use the visitors interface themselves. For example,
the `SelectEveryXthTest` visitor used in `pre-run modifier`_ examples could
be used like this:

.. sourcecode:: python

   from SelectEveryXthTest import SelectEveryXthTest

   ROBOT_LISTENER_API_VERSION = 3

   def start_suite(suite, result):
       selector = SelectEveryXthTest(x=2)
       suite.visit(selector)

Modifying results
'''''''''''''''''

Test execution results can be altered by modifying `test suite
<result.TestSuite_>`__ and `test case <result.TestCase_>`__ result objects
passed as the second argument to `start_suite` and `start_test` methods,
respectively, and by modifying the `message <result.Message_>`__ object passed
to the `log_message` method. This is demonstrated by the following listener
that is implemented as a class.

.. sourcecode:: python

    class ResultModifier(object):
        ROBOT_LISTENER_API_VERSION = 3

        def __init__(self, max_seconds=10):
            self.max_milliseconds = float(max_seconds) * 1000

        def start_suite(self, data, suite):
            suite.doc = 'Documentation set by listener.'
            # Information about tests only available via data at this point.
            smoke_tests = [test for test in data.tests if 'smoke' in test.tags]
            suite.metadata['Smoke tests'] = len(smoke_tests)

        def end_test(self, data, test):
            if test.status == 'PASS' and test.elapsedtime > self.max_milliseconds:
                test.status = 'FAIL'
                test.message = 'Test execution took too long.'

        def log_message(self, msg):
            if msg.level == 'WARN' and not msg.html:
                msg.message = '<b style="font-size: 1.5em">%s</b>' % msg.message
                msg.html = True

A limitation is that modifying the name of the current test suite or test
case is not possible because it has already been written to the `output.xml`_
file when listeners are called. Due to the same reason modifying already
finished tests in the `end_suite` method has no effect either.

This API is very similar to the `pre-Rebot modifier`_ API that can be used
to modify results before report and log are generated. The main difference is
that listeners modify also the created :file:`output.xml` file.

.. _library listeners:

Libraries as listeners
----------------------

Sometimes it is useful also for `test libraries`_ to get notifications about
test execution. This allows them, for example, to perform certain clean-up
activities automatically when a test suite or the whole test execution ends.

Registering listener
~~~~~~~~~~~~~~~~~~~~

A test library can register a listener by using `ROBOT_LIBRARY_LISTENER`
attribute. The value of this attribute should be an instance of the listener
to use. It may be a totally independent listener or the library itself can
act as a listener. To avoid listener methods to be exposed as keywords in
the latter case, it is possible to prefix them with an underscore.
For example, instead of using `end_suite` or `endSuite`, it is
possible to use `_end_suite` or `_endSuite`.

Following examples illustrates using an external listener as well as library
acting as a listener itself:

.. sourcecode:: java

   import my.project.Listener;


   public class JavaLibraryWithExternalListener {
       public static final Listener ROBOT_LIBRARY_LISTENER = new Listener();
       public static final String ROBOT_LIBRARY_SCOPE = "GLOBAL";
       public static final int ROBOT_LISTENER_API_VERSION = 2;

       // actual library code here ...
   }

.. sourcecode:: python

   class PythonLibraryAsListenerItself:
       ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
       ROBOT_LISTENER_API_VERSION = 2

       def __init__(self):
           self.ROBOT_LIBRARY_LISTENER = self

       def _end_suite(self, name, attrs):
           print('Suite %s (%s) ending.' % (name, attrs['id']))

       # actual library code here ...

As the seconds example above already demonstrated, library listeners have to
specify `listener interface versions`_ using `ROBOT_LISTENER_API_VERSION`
attribute exactly like any other listener.

It is also possible to specify multiple listeners for a single library by
giving `ROBOT_LIBRARY_LISTENER` a value as a list:

.. sourcecode:: python

   from listeners import Listener1, Listener2, Listener3


   class LibraryWithMultipleListeners:
       ROBOT_LIBRARY_LISTENER = [Listener1(), Listener2(), Listener3()]

       # actual library code here ...

Called listener methods
~~~~~~~~~~~~~~~~~~~~~~~

Library's listener will get notifications about all events in suites where
the library is imported. In practice this means that `start_suite`,
`end_suite`, `start_test`, `end_test`, `start_keyword`,
`end_keyword`, `log_message`, and `message` methods are
called inside those suites.

If the library creates a new listener instance every time when the library
itself is instantiated, the actual listener instance to use will change
according to the `library scope`_.
In addition to the previously listed listener methods, `close`
method is called when the library goes out of the scope.

See `Listener interface methods`_ section above for more information about
all these methods.
