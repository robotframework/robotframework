Listener interface
==================

Robot Framework's listener interface provides a powerful mechanism for getting
notifications and for inspecting and modifying data and results during execution.
Listeners are called, for example, when suites, tests and keywords start and end,
when output files are ready, and finally when the whole execution ends.
Example usages include communicating with external test management systems,
sending a message when a test fails, and modifying tests during execution.

Listeners are implemented as classes or modules with certain special methods.
They can be `taken into use from the command line`__ and be `registered
by libraries`__. The former listeners are active during the whole execution
while the latter are active only when executing suites where libraries registering
them are imported.

There are two supported listener interface versions, `listener version 2`_ and
`listener version 3`_. They have mostly the same methods, but these methods are
called with different arguments. The newer listener version 3 is more powerful
and generally recommended.

__ `Registering listeners from command line`_
__ `Libraries as listeners`_

.. contents::
   :depth: 2
   :local:

Listener structure
------------------

Listeners are implement as modules or classes `similarly as libraries`__.
They can implement certain named hook methods depending on what events they
are interested in. For example, if a listener wants to get a notification when
a test starts, it can implement the `start_test` method. As discussed in the
subsequent sections, different listener versions have slightly different set of
available methods and they also are called with different arguments.

__ `Creating test library class or module`_

.. sourcecode:: python

    # Listener implemented as a module using the listener API version 3.

    def start_suite(data, result):
        print(f"Suite '{data.name}' starting.")

    def end_test(data, result):
        print(f"Test '{result.name}' ended with status {result.status}.")

Listeners do not need to implement any explicit interface, it is enough to
simply implement needed methods and they will be recognized automatically.
There are, however, base classes `robot.api.interfaces.ListenerV2 <ListenerV2_>`__
and `robot.api.interfaces.ListenerV3 <ListenerV3_>`__ that can be used to get
method name completion in editors, type hints, and so on.

.. sourcecode:: python

    # Same as the above example, but uses an optional base class and type hints.

    from robot import result, running
    from robot.api.interfaces import ListenerV3


    class Example(ListenerV3):

        def start_suite(self, data: running.TestSuite, result: result.TestSuite):
            print(f"Suite '{data.name}' starting.")

        def end_test(self, data: running.TestCase, result: result.TestCase):
            print(f"Test '{result.name}' ended with status {result.status}.")

.. note:: Optional listener base classes are new in Robot Framework 6.1.

In addition to using "snake case" like `start_test` with listener method names,
it is possible to use "camel case" like `startTest`. This support was added
when it was possible to run Robot Framework on Jython and implement listeners
using Java. It is preserved for backwards compatibility reasons, but not
recommended with new listeners.

Listener interface versions
---------------------------

There are two supported listener interface versions with version numbers 2 and 3.
A listener can specify which version to use by having a `ROBOT_LISTENER_API_VERSION`
attribute with value 2 or 3, respectively. Starting from Robot Framework 7.0,
the listener version 3 is used by default if the version is not specified.

`Listener version 2`_ and `listener version 3`_ have mostly the same methods,
but arguments passed to these methods are different. Arguments given to listener 2
methods are strings and dictionaries containing information about execution. This
information can be inspected and sent further, but it is not possible to
modify it directly. Listener 3 methods get the same model objects that Robot Framework
itself uses, and these model objects can be both inspected and modified.

Listener version 3 is more powerful than the older listener version 2
and generally recommended.

Listener version 2
~~~~~~~~~~~~~~~~~~

Listeners using the listener API version 2 get notifications about various events
during execution, but they do not have access to actually executed tests and thus
cannot directly affect the execution or created results.

Listener methods in the API version 2 are listed in the following table
and in the API docs of the optional ListenerV2_ base class.
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
   |                  |                  | * `metadata`: `Free suite metadata`_ as a dictionary.          |
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
   | start_keyword    | name, attributes | Called when a keyword or a control structure such as `IF/ELSE` |
   |                  |                  | or `TRY/EXCEPT` starts.                                        |
   |                  |                  |                                                                |
   |                  |                  | With keywords `name` is the full keyword name containing       |
   |                  |                  | possible library or resource name as a prefix like             |
   |                  |                  | `MyLibrary.Example Keyword`. With control structures `name`    |
   |                  |                  | contains string representation of parameters.                  |
   |                  |                  |                                                                |
   |                  |                  | Keywords and control structures share most of attributes, but  |
   |                  |                  | control structures can have additional attributes depending    |
   |                  |                  | on their `type`.                                               |
   |                  |                  |                                                                |
   |                  |                  | Shared attributes:                                             |
   |                  |                  |                                                                |
   |                  |                  | * `type`: String specifying type of the started item. Possible |
   |                  |                  |   values are: `KEYWORD`, `SETUP`, `TEARDOWN`, `FOR`, `WHILE`,  |
   |                  |                  |   `ITERATION`, `IF`, `ELSE IF`, `ELSE`, `TRY`, `EXCEPT`,       |
   |                  |                  |   `FINALLY`, `VAR`, `RETURN`, `BREAK`, `CONTINUE` and `ERROR`. |
   |                  |                  |   All type values were changed in RF 4.0 and in RF 5.0         |
   |                  |                  |   `FOR ITERATION` was changed to `ITERATION`.                  |
   |                  |                  | * `kwname`: Name of the keyword without library or             |
   |                  |                  |   resource prefix. String representation of parameters with    |
   |                  |                  |   control structures.                                          |
   |                  |                  | * `libname`: Name of the library or resource file the keyword  |
   |                  |                  |   belongs to. An empty string with user keywords in a test     |
   |                  |                  |   case file and with control structures.                       |
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
   |                  |                  |                                                                |
   |                  |                  | Additional attributes for `FOR` types:                         |
   |                  |                  |                                                                |
   |                  |                  | * `variables`: Assigned variables for each loop iteration      |
   |                  |                  |   as a list or strings.                                        |
   |                  |                  | * `flavor`: Type of loop (e.g. `IN RANGE`).                    |
   |                  |                  | * `values`: List of values being looped over                   |
   |                  |                  |   as a list or strings.                                        |
   |                  |                  | * `start`: Start configuration. Only used with `IN ENUMERATE`  |
   |                  |                  |   loops. New in RF 6.1.                                        |
   |                  |                  | * `mode`: Mode configuration. Only used with `IN ZIP` loops.   |
   |                  |                  |   New in RF 6.1.                                               |
   |                  |                  | * `fill`: Fill value configuration. Only used with `IN ZIP`    |
   |                  |                  |   loops. New in RF 6.1.                                        |
   |                  |                  |                                                                |
   |                  |                  | Additional attributes for `ITERATION` types with `FOR` loops:  |
   |                  |                  |                                                                |
   |                  |                  | * `variables`: Variables and string representations of their   |
   |                  |                  |   contents for one `FOR` loop iteration as a dictionary.       |
   |                  |                  |                                                                |
   |                  |                  | Additional attributes for `WHILE` types:                       |
   |                  |                  |                                                                |
   |                  |                  | * `condition`: The looping condition.                          |
   |                  |                  | * `limit`: The maximum iteration limit.                        |
   |                  |                  | * `on_limit`: What to do if the limit is exceeded.             |
   |                  |                  |   Valid values are `pass` and `fail`. New in RF 7.0.           |
   |                  |                  | * `on_limit_message`: The custom error raised when the         |
   |                  |                  |   limit of the WHILE loop is reached. New in RF 6.1.           |
   |                  |                  |                                                                |
   |                  |                  | Additional attributes for `IF` and `ELSE IF` types:            |
   |                  |                  |                                                                |
   |                  |                  | * `condition`: The conditional expression being evaluated.     |
   |                  |                  |   With `ELSE IF` new in RF 6.1.                                |
   |                  |                  |                                                                |
   |                  |                  | Additional attributes for `EXCEPT` types:                      |
   |                  |                  |                                                                |
   |                  |                  | * `patterns`: The exception patterns being matched             |
   |                  |                  |   as a list or strings.                                        |
   |                  |                  | * `pattern_type`: The type of pattern match (e.g. `GLOB`).     |
   |                  |                  | * `variable`: The variable containing the captured exception.  |
   |                  |                  |                                                                |
   |                  |                  | Additional attributes for `RETURN` types:                      |
   |                  |                  |                                                                |
   |                  |                  | * `values`: Return values from a keyword as a list or strings. |
   |                  |                  |                                                                |
   |                  |                  | Additional attributes for `VAR` types:                         |
   |                  |                  |                                                                |
   |                  |                  | * `name`: Variable name.                                       |
   |                  |                  | * `value`: Variable value. A string with scalar variables and  |
   |                  |                  |   a list otherwise.                                            |
   |                  |                  | * `scope`: Variable scope (e.g. `GLOBAL`) as a string.         |
   |                  |                  |                                                                |
   |                  |                  | Additional attributes for control structures are in general    |
   |                  |                  | new in RF 6.0. `VAR` is new in RF 7.0.                         |
   +------------------+------------------+----------------------------------------------------------------+
   | end_keyword      | name, attributes | Called when a keyword or a control structure ends.             |
   |                  |                  |                                                                |
   |                  |                  | `name` is the full keyword name containing                     |
   |                  |                  | possible library or resource name as a prefix.                 |
   |                  |                  | For example, `MyLibrary.Example Keyword`.                      |
   |                  |                  |                                                                |
   |                  |                  | Control structures have additional attributes, which change    |
   |                  |                  | based on the `type` attribute. For descriptions of all         |
   |                  |                  | possible attributes, see the `start_keyword` section.          |
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
   |                  |                  | has been given a custom name when imported it using `AS`,      |
   |                  |                  | `name` is the specified alias.                                 |
   |                  |                  |                                                                |
   |                  |                  | Contents of the attribute dictionary:                          |
   |                  |                  |                                                                |
   |                  |                  | * `args`: Arguments passed to the library as a list.           |
   |                  |                  | * `originalname`: The original library name if the library has |
   |                  |                  |   been given an alias using `AS`, otherwise same as `name`.    |
   |                  |                  | * `source`: An absolute path to the library source. `None`     |
   |                  |                  |   if getting the                                               |
   |                  |                  |   source of the library failed for some reason.                |
   |                  |                  | * `importer`: An absolute path to the file importing the       |
   |                  |                  |   library. `None` when BuiltIn_ is imported as well as when    |
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
   |                  |                  | `path` is an absolute path to the file as a string.            |
   +------------------+------------------+----------------------------------------------------------------+
   | log_file         | path             | Called when writing to a `log file`_ is ready.                 |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file as a string.            |
   +------------------+------------------+----------------------------------------------------------------+
   | report_file      | path             | Called when writing to a `report file`_ is ready.              |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file as a string.            |
   +------------------+------------------+----------------------------------------------------------------+
   | xunit_file       | path             | Called when writing to an `xunit file`_ is ready.              |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file as a string.            |
   +------------------+------------------+----------------------------------------------------------------+
   | debug_file       | path             | Called when writing to a `debug file`_ is ready.               |
   |                  |                  |                                                                |
   |                  |                  | `path` is an absolute path to the file as a string.            |
   +------------------+------------------+----------------------------------------------------------------+
   | close            |                  | Called when the whole test execution ends.                     |
   |                  |                  |                                                                |
   |                  |                  | With `library listeners`_ called when the library goes out     |
   |                  |                  | of scope.                                                      |
   +------------------+------------------+----------------------------------------------------------------+

Listener version 3
~~~~~~~~~~~~~~~~~~

Listener version 3 has mostly the same methods as `listener version 2`_,
but arguments of the methods related to test execution are different.
These methods get actual running and result model objects that used by Robot
Framework itself, and listeners can both query information they need and
change the model objects on the fly.

Listener version 3 was enhanced heavily in Robot Framework 7.0 when it
got `methods related to keywords and control structures`__. It still does not
have methods related to library, resource file and variable file imports,
but `the plan is to add them in Robot Framework 7.1`__.

__ https://github.com/robotframework/robotframework/issues/3296
__ https://github.com/robotframework/robotframework/issues/5008

Listener version 3 has separate methods for library keywords, user keywords and
all control structures. If there is a need to listen to all keyword related
events, it is possible to implement `start_keyword` and `end_keyword`. In addition
to that, `start_body_item` and `end_body_item` can be implemented to get
notifications related to all keywords and control structures. These higher level
listener methods are not called if more specific methods like `start_library_keyword`
or `end_if` are implemented.

Listener methods in the API version 3 are listed in the following table
and in the API docs of the optional ListenerV3_ base class.

.. table:: Methods in the listener API 3
   :class: tabular

   +-----------------------+------------------+--------------------------------------------------------------------+
   |    Method             |    Arguments     |                          Documentation                             |
   +=======================+==================+====================================================================+
   | start_suite           | data, result     | Called when a test suite starts.                                   |
   |                       |                  |                                                                    |
   |                       |                  | `data` and `result` are model objects representing                 |
   |                       |                  | the `executed test suite <running.TestSuite_>`__ and `its          |
   |                       |                  | execution results <result.TestSuite_>`__, respectively.            |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_suite             | data, result     | Called when a test suite ends.                                     |
   |                       |                  |                                                                    |
   |                       |                  | Same arguments as with `start_suite`.                              |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | start_test            | data, result     | Called when a test case starts.                                    |
   |                       |                  |                                                                    |
   |                       |                  | `data` and `result` are model objects representing                 |
   |                       |                  | the `executed test case <running.TestCase_>`__ and `its            |
   |                       |                  | execution results <result.TestCase_>`__, respectively.             |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_test              | data, result     | Called when a test case ends.                                      |
   |                       |                  |                                                                    |
   |                       |                  | Same arguments as with `start_test`.                               |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | start_keyword         | data, result     | Called when a keyword starts.                                      |
   |                       |                  |                                                                    |
   |                       |                  | `data` and `result` are model objects representing                 |
   |                       |                  | the `executed keyword call <running.Keyword_>`__ and `its          |
   |                       |                  | execution results <result.Keyword_>`__, respectively.              |
   |                       |                  |                                                                    |
   |                       |                  | This method is called, by default, with user keywords, library     |
   |                       |                  | keywords and when a keyword call is invalid. It is not called      |
   |                       |                  | if a more specific `start_user_keyword`, `start_library_keyword`   |
   |                       |                  | or `start_invalid_keyword` method is implemented.                  |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_keyword           | data, result     | Called when a keyword ends.                                        |
   |                       |                  |                                                                    |
   |                       |                  | Same arguments and other semantics as with `start_keyword`.        |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | start_user_keyword    | data,            | Called when a user keyword starts.                                 |
   |                       | implementation,  |                                                                    |
   |                       | result           | `data` and `result` are the same as with `start_keyword` and       |
   |                       |                  | `implementation` is the actually executed `user keyword            |
   |                       |                  | <running.UserKeyword_>`__.                                         |
   |                       |                  |                                                                    |
   |                       |                  | If this method is implemented, `start_keyword` is not called       |
   |                       |                  | with user keywords.                                                |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_user_keyword      | data,            | Called when a user keyword ends.                                   |
   |                       | implementation,  |                                                                    |
   |                       | result           | Same arguments and other semantics as with `start_user_keyword`.   |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | start_library_keyword | data             | Called when a library keyword starts.                              |
   |                       | implementation,  |                                                                    |
   |                       | result           | `data` and `result` are the same as with `start_keyword` and       |
   |                       |                  | `implementation` represents the executed `library keyword          |
   |                       |                  | <running.LibraryKeyword_>`__.                                      |
   |                       |                  |                                                                    |
   |                       |                  | If this method is implemented, `start_keyword` is not called       |
   |                       |                  | with library keywords.                                             |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_library_keyword   | data,            | Called when a library keyword ends.                                |
   |                       | implementation,  |                                                                    |
   |                       | result           | Same arguments and other semantics as with                         |
   |                       |                  | `start_library_keyword`.                                           |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | start_invalid_keyword | data             | Called when an invalid keyword call starts.                        |
   |                       | implementation,  |                                                                    |
   |                       | result           | `data` and `result` are the same as with `start_keyword` and       |
   |                       |                  | `implementation` represents the `invalid keyword call              |
   |                       |                  | <running.InvalidKeyword_>`__. Keyword may not have been found,     |
   |                       |                  | there could have been multiple matches, or the keyword call        |
   |                       |                  | itself could have been invalid.                                    |
   |                       |                  |                                                                    |
   |                       |                  | If this method is implemented, `start_keyword` is not called       |
   |                       |                  | with invalid keyword calls.                                        |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_invalid_keyword   | data,            | Called when an invalid keyword call ends.                          |
   |                       | implementation,  |                                                                    |
   |                       | result           | Same arguments and other semantics as with                         |
   |                       |                  | `start_invalid_keyword`.                                           |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | start_for,            | data, result     | Called when control structures start.                              |
   | start_for_iteration,  |                  |                                                                    |
   | start_while,          |                  | See the documentation and type hints of the optional               |
   | start_while_iteration,|                  | `ListenerV3`_ base class for more information.                     |
   | start_if,             |                  |                                                                    |
   | start_if_branch,      |                  |                                                                    |
   | start_try,            |                  |                                                                    |
   | start_try_branch,     |                  |                                                                    |
   | start_var,            |                  |                                                                    |
   | start_continue,       |                  |                                                                    |
   | start_break,          |                  |                                                                    |
   | start_return          |                  |                                                                    |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_for,              | data, result     | Called when control structures end.                                |
   | end_for_iteration,    |                  |                                                                    |
   | end_while,            |                  | See the documentation and type hints of the optional               |
   | end_while_iteration,  |                  | `ListenerV3`_ base class for more information.                     |
   | end_if,               |                  |                                                                    |
   | end_if_branch,        |                  |                                                                    |
   | end_try,              |                  |                                                                    |
   | end_try_branch,       |                  |                                                                    |
   | end_var,              |                  |                                                                    |
   | end_continue,         |                  |                                                                    |
   | end_break,            |                  |                                                                    |
   | end_return            |                  |                                                                    |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | start_error           | data, result     | Called when invalid syntax starts.                                 |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_error             | data, result     | Called when invalid syntax ends.                                   |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | start_body_item       | data, result     | Called when a keyword or a control structure starts, unless        |
   |                       |                  | a more specific method such as `start_keyword` or `start_if`       |
   |                       |                  | is implemented.                                                    |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | end_body_item         | data, result     | Called when a keyword or a control structure ends, unless          |
   |                       |                  | a more specific method such as `end_keyword` or `end_if`           |
   |                       |                  | is implemented.                                                    |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | log_message           | message          | Called when an executed keyword writes a log message.              |
   |                       |                  | `message` is a model object representing the `logged               |
   |                       |                  | message <result.Message_>`__.                                      |
   |                       |                  |                                                                    |
   |                       |                  | This method is not called if the message has level below           |
   |                       |                  | the current `threshold level <Log levels_>`__.                     |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | message               | message          | Called when the framework itself writes a syslog_ message.         |
   |                       |                  |                                                                    |
   |                       |                  | `message` is same object as with `log_message`.                    |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | library_import        | N/A              | Not currently implemented.                                         |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | resource_import       | N/A              | Not currently implemented.                                         |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | variables_import      | N/A              | Not currently implemented.                                         |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | output_file           | path             | Called when writing to an `output file`_ is ready.                 |
   |                       |                  |                                                                    |
   |                       |                  | `path` is an absolute path to the file as a `pathlib.Path` object. |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | log_file              | path             | Called when writing to a `log file`_ is ready.                     |
   |                       |                  |                                                                    |
   |                       |                  | `path` is an absolute path to the file as a `pathlib.Path` object. |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | report_file           | path             | Called when writing to a `report file`_ is ready.                  |
   |                       |                  |                                                                    |
   |                       |                  | `path` is an absolute path to the file as a `pathlib.Path` object. |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | xunit_file            | path             | Called when writing to an `xunit file`_ is ready.                  |
   |                       |                  |                                                                    |
   |                       |                  | `path` is an absolute path to the file as a `pathlib.Path` object. |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | debug_file            | path             | Called when writing to a `debug file`_ is ready.                   |
   |                       |                  |                                                                    |
   |                       |                  | `path` is an absolute path to the file as a `pathlib.Path` object. |
   +-----------------------+------------------+--------------------------------------------------------------------+
   | close                 |                  | Called when the whole test execution ends.                         |
   |                       |                  |                                                                    |
   |                       |                  | With `library listeners`_ called when the library goes out         |
   |                       |                  | of scope.                                                          |
   +-----------------------+------------------+--------------------------------------------------------------------+

.. note:: Prior to Robot Framework 7.0, paths passed to result file related listener
          version 3 methods were strings.

Taking listeners into use
-------------------------

Registering listeners from command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listeners that need to be active during the whole execution must be taken into
use from the command line. That is done using the :option:`--listener` option
so that the name of the listener is given to it as an argument. The listener
name is got from the name of the class or module implementing the
listener, similarly as `library name`_ is got from the class or module
implementing the library. The specified listeners must be in the same `module
search path`_ where test libraries are searched from when they are imported.
In addition to registering a listener by using a name, it is possible to give
an absolute or a relative path to the listener file `similarly as with test
libraries`__. It is possible to take multiple listeners
into use by using this option several times::

   robot --listener MyListener tests.robot
   robot --listener path/to/MyListener.py tests.robot
   robot --listener module.Listener --listener AnotherListener tests.robot

It is also possible to give arguments to listener classes from the command
line. Arguments are specified after the listener name (or path) using a colon
(`:`) as a separator. If a listener is given as an absolute Windows path,
the colon after the drive letter is not considered a separator.
Additionally, it is possible to use a semicolon (`;`) as an
alternative argument separator. This is useful if listener arguments
themselves contain colons, but requires surrounding the whole value with
quotes on UNIX-like operating systems::

   robot --listener listener.py:arg1:arg2 tests.robot
   robot --listener "listener.py;arg:with:colons" tests.robot
   robot --listener c:\path\listener.py;d:\first\arg;e:\second\arg tests.robot

In addition to passing arguments one-by-one as positional arguments, it is
possible to pass them using the `named argument syntax`_ similarly as when using
keywords::

   robot --listener listener.py:name=value tests.robot
   robot --listener "listener.py;name=value:with:colons;second=argument" tests.robot

Listener arguments are automatically converted using `same rules as with
keywords`__ based on `type hints`__ and `default values`__. For example,
this listener

.. sourcecode:: python

    class Listener:

        def __init__(self, port: int, log=True):
            self.port = post
            self.log = log

could be used like ::

    robot --listener Listener:8270:false

and the first argument would be converted to an integer based on the type hint
and the second to a Boolean based on the default value.

.. note:: Both the named argument syntax and argument conversion are new in
          Robot Framework 4.0.

__ `Using physical path to library`_
__ `Supported conversions`_
__ `Specifying argument types using function annotations`_
__ `Implicit argument types based on default values`_

.. _library listeners:

Libraries as listeners
~~~~~~~~~~~~~~~~~~~~~~

Sometimes it is useful also for `test libraries`_ to get notifications about
test execution. This allows them, for example, to perform certain clean-up
activities automatically when a test suite or the whole test execution ends.

Registering listener
''''''''''''''''''''

A test library can register a listener by using the `ROBOT_LIBRARY_LISTENER`
attribute. The value of this attribute should be an instance of the listener
to use. It may be a totally independent listener or the library itself can
act as a listener. To avoid listener methods to be exposed as keywords in
the latter case, it is possible to prefix them with an underscore.
For example, instead of using `end_suite` it is possible to use `_end_suite`.

Following examples illustrates using an external listener as well as a library
acting as a listener itself:

.. sourcecode:: python

   from listener import Listener


   class LibraryWithExternalListener:
       ROBOT_LIBRARY_SCOPE = 'GLOBAL'
       ROBOT_LIBRARY_LISTENER = Listener()

       def example_keyword(self):
            ...

.. sourcecode:: python

   class LibraryItselfAsListener:
       ROBOT_LIBRARY_SCOPE = 'SUITE'
       ROBOT_LISTENER_API_VERSION = 2

       def __init__(self):
           self.ROBOT_LIBRARY_LISTENER = self

       # Use the '_' prefix to avoid listener method becoming a keyword.
       def _end_suite(self, name, attrs):
           print(f"Suite '{name}' ending with status {attrs['id']}.")

       def example_keyword(self):
            ...

As the second example above already demonstrated, library listeners can
specify `listener interface versions`_ using the `ROBOT_LISTENER_API_VERSION`
attribute exactly like any other listener.

Starting from Robot Framework 7.0, a listener can register itself to be a listener
also by using a string `SELF` (case-insensitive) as a listener. This is especially
convenient when using the `@library decorator`_:

.. sourcecode:: python

   from robot.api.deco import keyword, library


   @library(scope='SUITE', listener='SELF')
   class LibraryItselfAsListener:

       # Listener version is not specified, so uses the listener version 3 by default.
       # When using the @library decorator, keywords must use the @keyword decorator,
       # so there is no need to use the '_' prefix here.
       def end_suite(self, data, result):
           print(f"Suite '{data.name}' ending with status {result.status}.")

       @keyword
       def example_keyword(self):
            ...

It is also possible to specify multiple listeners for a single library by
giving `ROBOT_LIBRARY_LISTENER` a value as a list:

.. sourcecode:: python

   from listeners import Listener1, Listener2, Listener3


   class LibraryWithMultipleListeners:
       ROBOT_LIBRARY_LISTENER = [Listener1(), Listener2(), Listener3()]

       def example_keyword(self):
            ...

Called listener methods
'''''''''''''''''''''''

Library listeners get notifications about all events in suites where
libraries using them are imported. In practice this means that suite,
test, keyword, control structure and log message related methods are
called. In addition to them, the `close` method is called when the library
goes out of the scope.

If library creates a new listener instance every time when the library
itself is instantiated, the actual listener instance to use will change
according to the `library scope`_.

Listener examples
-----------------

This section contains examples using the listener interface. First examples
illustrate getting notifications durin execution and latter examples modify
executed tests and created results.

Getting information
~~~~~~~~~~~~~~~~~~~

The first example is implemented as a Python module. It uses the `listener
version 2`_, but could equally well be implemented by using the `listener
version 3`_.

.. sourcecode:: python

   """Listener that stops execution if a test fails."""

   ROBOT_LISTENER_API_VERSION = 2

   def end_test(name, attrs):
       if attrs['status'] == 'FAIL':
           print(f"Test '{name}'" failed: {attrs['message']}")
           input("Press enter to continue.")

If the above example would be saved to, for example, :file:`PauseExecution.py`
file, it could be used from the command line like this::

   robot --listener path/to/PauseExecution.py tests.robot

The next example, which still uses the listener version 2, is slightly more
complicated. It writes all the information it gets into a text file in
a temporary directory without much formatting. The filename may be given
from the command line, but it also has a default value. Note that in real usage,
the `debug file`_ functionality available through the command line option
:option:`--debugfile` is probably more useful than this example.

.. sourcecode:: python

   import os.path
   import tempfile


   class Example:
       ROBOT_LISTENER_API_VERSION = 2

       def __init__(self, file_name='listen.txt'):
           path = os.path.join(tempfile.gettempdir(), file_name)
           self.file = open(path, 'w')

       def start_suite(self, name, attrs):
           self.file.write("%s '%s'\n" % (name, attrs['doc']))

       def start_test(self, name, attrs):
           tags = ' '.join(attrs['tags'])
           self.file.write("- %s '%s' [ %s ] :: " % (name, attrs['doc'], tags))

       def end_test(self, name, attrs):
           if attrs['status'] == 'PASS':
               self.file.write('PASS\n')
           else:
               self.file.write('FAIL: %s\n' % attrs['message'])

       def end_suite(self, name, attrs):
            self.file.write('%s\n%s\n' % (attrs['status'], attrs['message']))

       def close(self):
            self.file.close()

Modifying data and results
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following examples illustrate how to modify the executed tests and suites
as well as the execution results. All these examples require using
the `listener version 3`_.

Modifying executed suites and tests
'''''''''''''''''''''''''''''''''''

Changing what is executed is as easy as modifying the model objects representing
executed data passed to listener methods. This is illustrated by the example below that
adds a new test to each executed suite and a new keyword call to each test.

.. sourcecode:: python

   def start_suite(data, result):
       data.tests.create(name='New test')

   def start_test(data, result):
       data.body.create_keyword(name='Log', args=['Keyword added by listener!'])

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


   def start_suite(suite, result):
       selector = SelectEveryXthTest(x=2)
       suite.visit(selector)

Accessing library or resource file
''''''''''''''''''''''''''''''''''

It is possible to get more information about the actually executed keyword and
the library or resource file it belongs to:

.. sourcecode:: python

    from robot.running import Keyword as KeywordData, LibraryKeyword
    from robot.result import Keyword as KeywordResult


    def start_library_keyword(data: KeywordData,
                              implementation: LibraryKeyword,
                              result: KeywordResult):
        library = implementation.owner
        print(f"Keyword '{implementation.name}' is implemented in library "
              f"'{library.name}' at '{implementation.source}' on line "
              f"{implementation.lineno}. The library has {library.scope.name} "
              f"scope and the current instance is {library.instance}.")

As the above example illustrates, it is possible to get an access to the actual
library instance. This means that listeners can inspect the library state and also
modify it. With user keywords it is even possible to modify the keyword itself or,
via the `owner` resource file, any other keyword in the resource file.

Modifying results
'''''''''''''''''

Test execution results can be altered by modifying the result objects passed to
listener methods. This is demonstrated by the following listener that is implemented
as a class and also uses type hints:

.. sourcecode:: python

    from robot import result, running


    class ResultModifier:

        def __init__(self, max_seconds: float = 10.0):
            self.max_seconds = max_seconds

        def start_suite(self, data: running.TestSuite, result: result.TestSuite):
            result.doc = 'Documentation set by listener.'
            # Information about tests only available via data at this point.
            smoke_tests = [test for test in data.tests if 'smoke' in test.tags]
            result.metadata['Smoke tests'] = len(smoke_tests)

        def end_test(self, data: running.TestCase, result: result.TestCase):
            elapsed_seconds = result.elapsed_time.total_seconds()
            if result.status == 'PASS' and  elapsed_seconds > self.max_milliseconds:
                result.status = 'FAIL'
                result.message = 'Test execution took too long.'

        def log_message(self, msg: result.Message):
            if msg.level == 'WARN' and not msg.html:
                msg.message = f'<b style="font-size: 1.5em">{msg.message}</b>'
                msg.html = True

A limitation is that modifying the name of the current test suite or test
case is not possible because it has already been written to the `output.xml`_
file when listeners are called. Due to the same reason modifying already
finished tests in the `end_suite` method has no effect either.

Notice that although listeners can change status of any executed keyword or control
structure, that does not directly affect the status of the executed test. In general
listeners cannot directly fail keywords so that execution would stop or handle
failures so that execution would continue. This kind of functionality may be
added in the future if there are needs.

This API is very similar to the `pre-Rebot modifier`_ API that can be used
to modify results before report and log are generated. The main difference is
that listeners modify also the created :file:`output.xml` file.

More examples
~~~~~~~~~~~~~

Keyword and control structure related listener version 3 methods are so versatile
that covering them fully here in the User Guide is not possible. For more examples,
you can see the `acceptance tests`__ using theses methods in various ways.

__ https://github.com/robotframework/robotframework/tree/master/atest/testdata/output/listener_interface/body_items_v3
