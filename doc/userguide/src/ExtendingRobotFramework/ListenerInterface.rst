Using listener interface
------------------------

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
~~~~~~~~~~~~~~~~~~~~~~~~~

Listeners are taken into use from the command line with the :opt:`--listener`
option, so that the name of the listener is given to it as an argument. The
listener name is got from the name of the class or module implementing the
listener interface, similarly as `test library names`_ are got from classes
implementing them. The specified listeners must be in the same `module search
path`_ where test libraries are searched from when they are imported. Other
option is to give an absolute or a relative path to the listener file
`similarly as with test libraries`__. It is possible to take multiple listeners
into use by using this option several times.

It is also possible to give arguments to listener classes from the
command line. Arguments are specified after the listener name (or
path) using a colon as a separator. This approach provides only string
type arguments and arguments obviously cannot contain colons. However,
it should be pretty easy to listeners to go around these limitations.

__ `Using physical path to library`_

Examples::

   pybot --listener MyListener tests.html
   jybot --listener com.company.package.Listener tests.html
   pybot --listener path/to/MyListener.py tests.html
   pybot --listener module.Listener --listener AnotherListener tests.html
   pybot --listener ListenerWithArgs:arg1:arg2
   pybot --listener path/to/MyListener.java:argument tests.html

Available listener interface methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework creates an instance of the listener class with given arguments
when test execution starts. During the test execution, Robot Framework calls
listeners' methods when test suites, test cases and keywords start and end. It
also calls the appropriate methods when output files are ready, and finally at
the end it calls the :code:`close` method. A listener is not required to
implement any official interface, and it only needs to have the methods it
actually needs.

Listener interface versions
'''''''''''''''''''''''''''

The signatures of methods related to test execution progress were changed in
Robot Framework 2.1. This change was made so that new information can be added
to listener interface without breaking existing listeners. The old signatures
will continue to work, but they will be deprecated in some future version, so
all new listeners should be implemented with signatures described in the table
below. The most recent detailed description of the old listener interface can
be found in User Guide of Robot Framework 2.0.4.

.. note:: A listener must have attribute :code:`ROBOT_LISTENER_API_VERSION`
  defined in order to be recognized as a new style listener. Value of the
  :code:`ROBOT_LISTENER_API_VERSION` attribute must be 2, either as a string or
  as an integer. The examples below are implemented as new style listeners.

Listener interface method signatures
''''''''''''''''''''''''''''''''''''

All listener methods related to test execution progress have the same
signature :code:`method(name, attributes)`, where :code:`attributes`
is a dictionary containing details of the event. The following table
lists all the available methods in the listener interface and the
contents of the :code:`attributes` dictionary, where applicable. Keys
of the dictionary are strings. All of these methods have also
`camelCase` aliases.  Thus, for example, :code:`startSuite` is a
synonym to :code:`start_suite`.

.. table:: Available methods in the listener interface
   :class: tabular

   +---------------+------------------+--------------------------------------------------+
   |    Method     |    Arguments     |             Attributes / Explanation             |
   +===============+==================+==================================================+
   | start_suite   | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * longname: suite name including parent suites   |
   |               |                  | * doc: test suite documentation                  |
   |               |                  | * metadata: dictionary/map containing `free test |
   |               |                  |   suite metadata`_ (new in 2.5)                  |
   |               |                  | * source: absolute path of the file/directory    |
   |               |                  |   test suite was created from (new in 2.7)       |
   |               |                  | * suites: names of suites directly in this suite |
   |               |                  |   as a list of strings (new in 2.5)              |
   |               |                  | * tests: names of tests directly in this suite   |
   |               |                  |   as a list of strings (new in 2.5)              |
   |               |                  | * totaltests: total number of tests in this suite|
   |               |                  |   and all its sub-suites as an integer (new in   |
   |               |                  |   2.5)                                           |
   |               |                  | * starttime: execution start time                |
   +---------------+------------------+--------------------------------------------------+
   | end_suite     | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * longname: test suite name including parents    |
   |               |                  | * doc: test suite documentation                  |
   |               |                  | * metadata: dictionary/map containing `free test |
   |               |                  |   suite metadata`_ (new in 2.6)                  |
   |               |                  | * source: absolute path of the file/directory    |
   |               |                  |   test suite was created from (new in 2.7)       |
   |               |                  | * starttime: execution start time                |
   |               |                  | * endtime: execution end time                    |
   |               |                  | * elapsedtime: execution time in milliseconds    |
   |               |                  |   as an integer                                  |
   |               |                  | * status: either :code:`PASS` or :code:`FAIL`    |
   |               |                  | * statistics: suite statistics (number of passed |
   |               |                  |   and failed tests in the suite) as a string     |
   |               |                  | * message: error message if the suite setup or   |
   |               |                  |   teardown has failed, empty otherwise           |
   +---------------+------------------+--------------------------------------------------+
   | start_test    | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * longname: test name including parent suites    |
   |               |                  | * doc: test case documentation                   |
   |               |                  | * tags: test case tags as a list of strings      |
   |               |                  | * critical: :code:`yes` or :code:`no` depending  |
   |               |                  |   is test considered critical or not (new in 2.6)|
   |               |                  | * template: contains the name of the template    |
   |               |                  |   used for the test. If the test is not templated|
   |               |                  |   it will be an empty string (new in 2.6)        |
   |               |                  | * starttime: execution start time                |
   +---------------+------------------+--------------------------------------------------+
   | end_test      | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * longname: test name including parent suites    |
   |               |                  | * doc: test case documentation                   |
   |               |                  | * tags: test case tags as a list of strings      |
   |               |                  | * critical: :code:`yes` or :code:`no` depending  |
   |               |                  |   is test considered critical or not (new in 2.6)|
   |               |                  | * template: contains the name of the template    |
   |               |                  |   used for the test. If the test is not templated|
   |               |                  |   it will be an empty string (new in 2.6)        |
   |               |                  | * starttime: execution start time                |
   |               |                  | * endtime: execution end time                    |
   |               |                  | * elapsedtime: execution time in milliseconds    |
   |               |                  |   as an integer                                  |
   |               |                  | * status: either :code:`PASS` or :code:`FAIL`    |
   |               |                  | * message: status message, normally an error     |
   |               |                  |   message or an empty string                     |
   +---------------+------------------+--------------------------------------------------+
   | start_keyword | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * type: string :code:`Keyword` for normal        |
   |               |                  |   keywords and :code:`Test Setup`, :code:`Test   |
   |               |                  |   Teardown`, :code:`Suite Setup` or :code:`Suite |
   |               |                  |   Teardown` for keywords used in suite/test      |
   |               |                  |   setup/teardown (new in 2.6)                    |
   |               |                  | * doc: keyword documentation                     |
   |               |                  | * args: keyword's arguments as a list of strings |
   |               |                  | * starttime: execution start time                |
   +---------------+------------------+--------------------------------------------------+
   | end_keyword   | name, attributes | Keys in the attribute dictionary:                |
   |               |                  |                                                  |
   |               |                  | * type: same as with :code:`start_keyword`       |
   |               |                  | * doc: keyword documentation                     |
   |               |                  | * args: keyword's arguments as a list of strings |
   |               |                  | * starttime: execution start time                |
   |               |                  | * endtime: execution end time                    |
   |               |                  | * elapsedtime: execution time in milliseconds    |
   |               |                  |   as an integer                                  |
   |               |                  | * status: either :code:`PASS` or :code:`FAIL`    |
   +---------------+------------------+--------------------------------------------------+
   | log_message   | message          | Called when an executed keyword writes a log     |
   |               |                  | message. :code:`message` is a dictionary with    |
   |               |                  | the following keys:                              |
   |               |                  |                                                  |
   |               |                  | * message: the content of the message            |
   |               |                  | * level: `log level`_ used in logging the message|
   |               |                  | * timestamp: message creation time, format is    |
   |               |                  |   :code:`YYYY-MM-DD hh:mm:ss.mil`                |
   |               |                  | * html: string :code:`yes` or :code:`no` denoting|
   |               |                  |   whether the message should be interpreted as   |
   |               |                  |   HTML or not                                    |
   +---------------+------------------+--------------------------------------------------+
   | message       | message          | Called when the framework itself writes a syslog_|
   |               |                  | message. :code:`message` is a dictionary with    |
   |               |                  | same keys as with :code:`log_message` method.    |
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
interface specification below. Contents of the :code:`java.util.Map attributes` are
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
~~~~~~~~~~~~~~~~~

Robot Framework 2.6 introduced new `programmatic logging APIs`_ that
also listeners can utilize. There are some limitations, however, and
how different listener methods can log messages is explained in the
table below.

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
          listener methods :code:`log_message` and :code:`message`.

.. warning:: There were severe problems with listeners logging prior
             to Robot Framework 2.6.2. Using this functionality with
             earlier versions is thus not recommended.

Listener examples
~~~~~~~~~~~~~~~~~

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
functionality available through the command line option :opt:`--debugfile` is
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
