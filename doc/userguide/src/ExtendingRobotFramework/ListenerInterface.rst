Using listener interface
========================

Robot Framework has a listener interface that can be used to receive
notifications about test execution. Listeners are classes or modules
with certain special methods, and they can be implemented both with
Python and Java. Example uses of the listener interface include
external test monitors, sending a mail message when a test fails, and
communicating with other systems.

.. contents::
   :depth: 2
   :local:

Taking listeners into use
-------------------------

Listeners are taken into use from the command line with the :option:`--listener`
option, so that the name of the listener is given to it as an argument. The
listener name is got from the name of the class or module implementing the
listener interface, similarly as `test library names`_ are got from classes
implementing them. The specified listeners must be in the same `module search
path`_ where test libraries are searched from when they are imported. Other
option is to give an absolute or a relative path to the listener file
`similarly as with test libraries`__. It is possible to take multiple listeners
into use by using this option several times::

   pybot --listener MyListener tests.robot
   jybot --listener com.company.package.Listener tests.robot
   pybot --listener path/to/MyListener.py tests.robot
   pybot --listener module.Listener --listener AnotherListener tests.robot

It is also possible to give arguments to listener classes from the command
line. Arguments are specified after the listener name (or path) using a colon
(`:`) as a separator. If a listener is given as an absolute Windows path,
the colon after the drive letter is not considered a separator. Starting from
Robot Framework 2.8.7, it is possible to use a semicolon (`;`) as an
alternative argument separator. This is useful if listener arguments
themselves contain colons, but requires surrounding the whole value with
quotes on UNIX-like operating systems::

   pybot --listener listener.py:arg1:arg2 tests.robot
   pybot --listener "listener.py;arg:with:colons" tests.robot
   pybot --listener C:\\Path\\Listener.py;D:\\data;E:\\extra tests.robot

__ `Using physical path to library`_

Available listener interface methods
------------------------------------

Robot Framework creates an instance of the listener class with given arguments
when test execution starts. During the test execution, Robot Framework calls
listeners' methods when test suites, test cases and keywords start and end. It
also calls the appropriate methods when output files are ready, and finally at
the end it calls the `close` method. A listener is not required to
implement any official interface, and it only needs to have the methods it
actually needs.

Listener interface versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The signatures of methods related to test execution progress were changed in
Robot Framework 2.1. This change was made to allow new information to be added
to the listener interface without breaking existing listeners.
A listener must have attribute `ROBOT_LISTENER_API_VERSION` with value 2,
either as a string or as an integer, to be recognized as a new style listener.
The old listener interface has been deprecated in Robot Framework 2.9 and
will be removed in the next major release.

All new listeners should be implemented as new style listeners with method
signatures described in the next section. Also all following examples
are implemented as new style listeners. Documentation of the old listener
interface API can be found from `Robot Framework User Guide`__ version 2.0.4.

__ http://robotframework.org/robotframework/#user-guide

Listener interface method signatures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All listener methods related to test execution progress have the same
signature `method(name, attributes)`, where `attributes`
is a dictionary containing details of the event. The following table
lists all the available methods in the listener interface and the
contents of the `attributes` dictionary, where applicable. Keys
of the dictionary are strings. All of these methods have also
`camelCase` aliases.  Thus, for example, `startSuite` is a
synonym to `start_suite`.

.. table:: Available methods in the listener interface
   :class: tabular

   +---------------+------------------+--------------------------------------------------+
   |    Method     |    Arguments     |             Attributes / Explanation             |
   +===============+==================+==================================================+
   | start_suite   | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * id: suite id. 's1' for top level suite, 's1-s1'|
   |               |                  |   for its first child suite, 's1-s2' for second  |
   |               |                  |   child, and so on. (new in 2.8.5)               |
   |               |                  | * longname: suite name including parent suites   |
   |               |                  | * doc: test suite documentation                  |
   |               |                  | * metadata: dictionary/map containing `free test |
   |               |                  |   suite metadata`_                               |
   |               |                  | * source: absolute path of the file/directory    |
   |               |                  |   test suite was created from (new in 2.7)       |
   |               |                  | * suites: names of suites directly in this suite |
   |               |                  |   as a list of strings                           |
   |               |                  | * tests: names of tests directly in this suite   |
   |               |                  |   as a list of strings                           |
   |               |                  | * totaltests: total number of tests in this suite|
   |               |                  |   and all its sub-suites as an integer           |
   |               |                  | * starttime: execution start time                |
   +---------------+------------------+--------------------------------------------------+
   | end_suite     | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * id: suite id. 's1' for top level suite, 's1-s1'|
   |               |                  |   for its first child suite, 's1-s2' for second  |
   |               |                  |   child, and so on. (new in 2.8.5)               |
   |               |                  | * longname: test suite name including parents    |
   |               |                  | * doc: test suite documentation                  |
   |               |                  | * metadata: dictionary/map containing `free test |
   |               |                  |   suite metadata`_                               |
   |               |                  | * source: absolute path of the file/directory    |
   |               |                  |   test suite was created from (new in 2.7)       |
   |               |                  | * starttime: execution start time                |
   |               |                  | * endtime: execution end time                    |
   |               |                  | * elapsedtime: execution time in milliseconds    |
   |               |                  |   as an integer                                  |
   |               |                  | * status: either `PASS` or `FAIL`                |
   |               |                  | * statistics: suite statistics (number of passed |
   |               |                  |   and failed tests in the suite) as a string     |
   |               |                  | * message: error message if the suite setup or   |
   |               |                  |   teardown has failed, empty otherwise           |
   +---------------+------------------+--------------------------------------------------+
   | start_test    | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * id: test id in format like 's1-s2-t2', where   |
   |               |                  |   beginning is parent suite id and last part     |
   |               |                  |   shows test index in that suite (new in 2.8.5)  |
   |               |                  | * longname: test name including parent suites    |
   |               |                  | * doc: test case documentation                   |
   |               |                  | * tags: test case tags as a list of strings      |
   |               |                  | * critical: `yes` or `no` depending              |
   |               |                  |   is test considered critical or not             |
   |               |                  | * template: contains the name of the template    |
   |               |                  |   used for the test. If the test is not templated|
   |               |                  |   it will be an empty string                     |
   |               |                  | * starttime: execution start time                |
   +---------------+------------------+--------------------------------------------------+
   | end_test      | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * id: test id in format like 's1-s2-t2', where   |
   |               |                  |   beginning is parent suite id and last part     |
   |               |                  |   shows test index in that suite (new in 2.8.5)  |
   |               |                  | * longname: test name including parent suites    |
   |               |                  | * doc: test case documentation                   |
   |               |                  | * tags: test case tags as a list of strings      |
   |               |                  | * critical: `yes` or `no` depending              |
   |               |                  |   is test considered critical or not             |
   |               |                  | * template: contains the name of the template    |
   |               |                  |   used for the test. If the test is not templated|
   |               |                  |   it will be an empty string                     |
   |               |                  | * starttime: execution start time                |
   |               |                  | * endtime: execution end time                    |
   |               |                  | * elapsedtime: execution time in milliseconds    |
   |               |                  |   as an integer                                  |
   |               |                  | * status: either `PASS` or `FAIL`                |
   |               |                  | * message: status message, normally an error     |
   |               |                  |   message or an empty string                     |
   +---------------+------------------+--------------------------------------------------+
   | start_keyword | name, attributes | `name` is the full keyword name containing       |
   |               |                  | possible library or resource name as a prefix.   |
   |               |                  | For example, `MyLibrary.Example Keyword`.        |
   |               |                  |                                                  |
   |               |                  | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * type: string `Keyword` for normal              |
   |               |                  |   keywords and `Test Setup`, `Test               |
   |               |                  |   Teardown`, `Suite Setup` or `Suite             |
   |               |                  |   Teardown` for keywords used in suite/test      |
   |               |                  |   setup/teardown                                 |
   |               |                  | * kwname: name of the keyword without library or |
   |               |                  |   resource prefix (new in 2.9)                   |
   |               |                  | * libname: name of the library or resource the   |
   |               |                  |   keyword belongs to, or an empty string when    |
   |               |                  |   the keyword is in a test case file (new in 2.9)|
   |               |                  | * doc: keyword documentation                     |
   |               |                  | * args: keyword's arguments as a list of strings |
   |               |                  | * assign: list of variable names that keyword's  |
   |               |                  |   return value is assigned to (new in 2.9)       |
   |               |                  | * starttime: execution start time                |
   +---------------+------------------+--------------------------------------------------+
   | end_keyword   | name, attributes | `name` is the full keyword name containing       |
   |               |                  | possible library or resource name as a prefix.   |
   |               |                  | For example, `MyLibrary.Example Keyword`.        |
   |               |                  |                                                  |
   |               |                  | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * type: same as with `start_keyword`             |
   |               |                  | * kwname: name of the keyword without library or |
   |               |                  |   resource prefix (new in 2.9)                   |
   |               |                  | * libname: name of the library or resource the   |
   |               |                  |   keyword belongs to, or an empty string when    |
   |               |                  |   the keyword is in a test case file (new in 2.9)|
   |               |                  | * doc: keyword documentation                     |
   |               |                  | * args: keyword's arguments as a list of strings |
   |               |                  | * assign: list of variable names that keyword's  |
   |               |                  |   return value is assigned to (new in 2.9)       |
   |               |                  | * starttime: execution start time                |
   |               |                  | * endtime: execution end time                    |
   |               |                  | * elapsedtime: execution time in milliseconds    |
   |               |                  |   as an integer                                  |
   |               |                  | * status: either `PASS` or `FAIL`                |
   +---------------+------------------+--------------------------------------------------+
   | log_message   | message          | Called when an executed keyword writes a log     |
   |               |                  | message. `message` is a dictionary with          |
   |               |                  | the following keys:                              |
   |               |                  |                                                  |
   |               |                  | * message: the content of the message            |
   |               |                  | * level: `log level`_ used in logging the message|
   |               |                  | * timestamp: message creation time, format is    |
   |               |                  |   `YYYY-MM-DD hh:mm:ss.mil`                      |
   |               |                  | * html: string `yes` or `no` denoting            |
   |               |                  |   whether the message should be interpreted as   |
   |               |                  |   HTML or not                                    |
   +---------------+------------------+--------------------------------------------------+
   | message       | message          | Called when the framework itself writes a syslog_|
   |               |                  | message. `message` is a dictionary with          |
   |               |                  | same keys as with `log_message` method.          |
   +---------------+------------------+--------------------------------------------------+
   | output_file   | path             | Called when writing to an output file is         |
   |               |                  | finished. The path is an absolute path to the    |
   |               |                  | file.                                            |
   +---------------+------------------+--------------------------------------------------+
   | log_file      | path             | Called when writing to a log file is             |
   |               |                  | finished. The path is an absolute path to the    |
   |               |                  | file.                                            |
   +---------------+------------------+--------------------------------------------------+
   | report_file   | path             | Called when writing to a report file is          |
   |               |                  | finished. The path is an absolute path to the    |
   |               |                  | file.                                            |
   +---------------+------------------+--------------------------------------------------+
   | debug_file    | path             | Called when writing to a debug file is           |
   |               |                  | finished. The path is an absolute path to the    |
   |               |                  | file.                                            |
   +---------------+------------------+--------------------------------------------------+
   | close         |                  | Called after all test suites, and test cases in  |
   |               |                  | them, have been executed.                        |
   +---------------+------------------+--------------------------------------------------+

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

The first simple example is implemented in a Python module. It mainly
illustrates that using the listener interface is not very complicated.

.. sourcecode:: python

   ROBOT_LISTENER_API_VERSION = 2

   def start_test(name, attrs):
       print 'Executing test %s' % name

   def start_keyword(name, attrs):
       print 'Executing keyword %s with arguments %s' % (name, attrs['args'])

   def log_file(path):
       print 'Test log available at %s' % path

   def close():
       print 'All tests executed'

The second example, which still uses Python, is slightly more complicated. It
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

The third example implements the same functionality as the previous one, but uses Java instead of Python.

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

Test libraries as listeners
---------------------------

Sometimes it is useful also for `test libraries`_ to get notifications about
test execution. This allows them, for example, to perform certain clean-up
activities automatically when a test suite or the whole test execution ends.

.. note:: This functionality is new in Robot Framework 2.8.5.

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

       // actual library code here ...
   }

.. sourcecode:: python

   class PythonLibraryAsListenerItself(object):
       ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
       ROBOT_LISTENER_API_VERSION = 2

       def __init__(self):
           self.ROBOT_LIBRARY_LISTENER = self

       def _end_suite(self, name, attrs):
           print 'Suite %s (%s) ending.' % (name, attrs['id'])

       # actual library code here ...

As the seconds example above already demonstrated, library listeners can
specify `listener interface versions`_ using `ROBOT_LISTENER_API_VERSION`
attribute exactly like any other listener.

Starting from version 2.9, you can also provide any list like object of
instances in the `ROBOT_LIBRARY_LISTENER` attribute. This will cause all
instances of the list to be registered as listeners.

Called listener methods
~~~~~~~~~~~~~~~~~~~~~~~

Library's listener will get notifications about all events in suites where
the library is imported. In practice this means that `start_suite`,
`end_suite`, `start_test`, `end_test`, `start_keyword`,
`end_keyword`, `log_message`, and `message` methods are
called inside those suites.

If the library creates a new listener instance every time when the library
itself is instantiated, the actual listener instance to use will change
according to the `test library scope`_.
In addition to the previously listed listener methods, `close`
method is called when the library goes out of the scope.

See `Listener interface method signatures`_ section above
for more information about all these methods.
