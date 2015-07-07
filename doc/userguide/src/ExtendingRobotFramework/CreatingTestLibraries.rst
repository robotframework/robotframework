Creating test libraries
=======================

Robot Framework's actual testing capabilities are provided by test
libraries. There are many existing libraries, some of which are even
bundled with the core framework, but there is still often a need to
create new ones. This task is not too complicated because, as this
chapter illustrates, Robot Framework's library API is simple
and straightforward.

.. contents::
   :depth: 2
   :local:

Introduction
------------

Supported programming languages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework itself is written with Python_ and naturally test
libraries extending it can be implemented using the same
language. When running the framework on Jython_, libraries can also be
implemented using Java_. Pure Python code works both on Python and
Jython, assuming that it does not use syntax or modules that are not
available on Jython. When using Python, it is also possible to
implement libraries with C using `Python C API`__, although it is
often easier to interact with C code from Python libraries using
ctypes__ module.

Libraries implemented using these natively supported languages can
also act as wrappers to functionality implemented using other
programming languages. A good example of this approach is the `Remote
library`_, and another widely used approaches is running external
scripts or tools as separate processes.

.. tip:: `Python Tutorial for Robot Framework Test Library Developers`__
         covers enough of Python language to get started writing test
         libraries using it. It also contains a simple example library
         and test cases that you can execute and otherwise investigate
         on your machine.

__ http://docs.python.org/c-api/index.html
__ http://docs.python.org/library/ctypes.html
__ http://code.google.com/p/robotframework/wiki/PythonTutorial

Different test library APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework has three different test library APIs.

Static API

  The simplest approach is having a module (in Python) or a class
  (in Python or Java) with methods which map directly to
  `keyword names`_. Keywords also take the same `arguments`__ as
  the methods implementing them.  Keywords `report failures`__ with
  exceptions, `log`__ by writing to standard output and can `return
  values`__ using the `return` statement.

Dynamic API

  Dynamic libraries are classes that implement a method to get the names
  of the keywords they implement, and another method to execute a named
  keyword with given arguments. The names of the keywords to implement, as
  well as how they are executed, can be determined dynamically at
  runtime, but reporting the status, logging and returning values is done
  similarly as in the static API.

Hybrid API

  This is a hybrid between the static and the dynamic API. Libraries are
  classes with a method telling what keywords they implement, but
  those keywords must be available directly. Everything else except
  discovering what keywords are implemented is similar as in the
  static API.

All these APIs are described in this chapter. Everything is based on
how the static API works, so its functions are discussed first. How
the `dynamic library API`_ and the `hybrid library API`_ differ from it
is then discussed in sections of their own.

The examples in this chapter are mainly about using Python, but they
should be easy to understand also for Java-only developers. In those
few cases where APIs have differences, both usages are explained with
adequate examples.

__ `Keyword arguments`_
__ `Reporting keyword status`_
__ `Logging information`_
__ `Returning values`_

Creating test library class or module
-------------------------------------

Test libraries can be implemented as Python modules and Python or Java
classes.

Test library names
~~~~~~~~~~~~~~~~~~

The name of a test library that is used when a library is imported is
the same as the name of the module or class implementing it. For
example, if you have a Python module `MyLibrary` (that is,
file :file:`MyLibrary.py`), it will create a library with name
:name:`MyLibrary`. Similarly, a Java class `YourLibrary`, when
it is not in any package, creates a library with exactly that name.

Python classes are always inside a module. If the name of a class
implementing a library is the same as the name of the module, Robot
Framework allows dropping the class name when importing the
library. For example, class `MyLib` in :file:`MyLib.py`
file can be used as a library with just name :name:`MyLib`. This also
works with submodules so that if, for example, `parent.MyLib` module
has class `MyLib`, importing it using just :name:`parent.MyLib`
works. If the module name and class name are different, libraries must be
taken into use using both module and class names, such as
:name:`mymodule.MyLibrary` or :name:`parent.submodule.MyLib`.

Java classes in a non-default package must be taken into use with the
full name. For example, class `MyLib` in `com.mycompany.myproject`
package must be imported with name :name:`com.mycompany.myproject.MyLib`.

.. note:: Dropping class names with submodules works only in Robot Framework
          2.8.4 and newer. With earlier versions you need to include also
          the class name like :name:`parent.MyLib.MyLib`.

.. tip:: If the library name is really long, for example when the Java
         package name is long, it is recommended to give the library a
         simpler alias by using the `WITH NAME syntax`_.

Providing arguments to test libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All test libraries implemented as classes can take arguments. These
arguments are specified in the Setting table after the library name,
and when Robot Framework creates an instance of the imported library,
it passes them to its constructor. Libraries implemented as a module
cannot take any arguments, so trying to use those results in an error.

The number of arguments needed by the library is the same
as the number of arguments accepted by the library's
constructor. The default values and variable number of arguments work
similarly as with `keyword arguments`_, with the exception that there
is no variable argument support for Java libraries. Arguments passed
to the library, as well as the library name itself, can be specified
using variables, so it is possible to alter them, for example, from the
command line.

.. sourcecode:: robotframework

   *** Settings ***
   Library    MyLibrary     10.0.0.1    8080
   Library    AnotherLib    ${VAR}

Example implementations, first one in Python and second in Java, for
the libraries used in the above example:

.. sourcecode:: python

  from example import Connection

  class MyLibrary:

      def __init__(self, host, port=80):
          self._conn = Connection(host, int(port))

      def send_message(self, message):
          self._conn.send(message)

.. sourcecode:: java

   public class AnotherLib {

       private String setting = null;

       public AnotherLib(String setting) {
           setting = setting;
       }

       public void doSomething() {
           if setting.equals("42") {
               // do something ...
           }
       }
   }

Test library scope
~~~~~~~~~~~~~~~~~~

Libraries implemented as classes can have an internal state, which can
be altered by keywords and with arguments to the constructor of the
library. Because the state can affect how keywords actually behave, it
is important to make sure that changes in one test case do not
accidentally affect other test cases. These kind of dependencies may
create hard-to-debug problems, for example, when new test cases are
added and they use the library inconsistently.

Robot Framework attempts to keep test cases independent from each
other: by default, it creates new instances of test libraries for
every test case. However, this behavior is not always desirable,
because sometimes test cases should be able to share a common
state. Additionally, all libraries do not have a state and creating
new instances of them is simply not needed.

Test libraries can control when new libraries are created with a
class attribute `ROBOT_LIBRARY_SCOPE` . This attribute must be
a string and it can have the following three values:

`TEST CASE`
  A new instance is created for every test case. A possible suite setup
  and suite teardown share yet another instance. This is the default.

`TEST SUITE`
  A new instance is created for every test suite. The lowest-level test
  suites, created from test case files and containing test cases, have
  instances of their own, and higher-level suites all get their own instances
  for their possible setups and teardowns.

`GLOBAL`
  Only one instance is created during the whole test execution and it
  is shared by all test cases and test suites. Libraries created from
  modules are always global.

.. note:: If a library is imported multiple times with different arguments__,
          a new instance is created every time regardless the scope.

When the `TEST SUITE` or `GLOBAL` scopes are used with test
libraries that have a state, it is recommended that libraries have some
special keyword for cleaning up the state. This keyword can then be
used, for example, in a suite setup or teardown to ensure that test
cases in the next test suites can start from a known state. For example,
:name:`SeleniumLibrary` uses the `GLOBAL` scope to enable
using the same browser in different test cases without having to
reopen it, and it also has the :name:`Close All Browsers` keyword for
easily closing all opened browsers.

Example Python library using the `TEST SUITE` scope:

.. sourcecode:: python

    class ExampleLibrary:

        ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

        def __init__(self):
            self._counter = 0

        def count(self):
            self._counter += 1
            print self._counter

        def clear_counter(self):
            self._counter = 0

Example Java library using the `GLOBAL` scope:

.. sourcecode:: java

    public class ExampleLibrary {

        public static final String ROBOT_LIBRARY_SCOPE = "GLOBAL";

        private int counter = 0;

        public void count() {
            counter += 1;
            System.out.println(counter);
        }

        public void clearCounter() {
            counter = 0;
        }
    }

__ `Providing arguments to test libraries`_

Specifying library version
~~~~~~~~~~~~~~~~~~~~~~~~~~

When a test library is taken into use, Robot Framework tries to
determine its version. This information is then written into the syslog_
to provide debugging information. Library documentation tool
Libdoc_ also writes this information into the keyword
documentations it generates.

Version information is read from attribute
`ROBOT_LIBRARY_VERSION`, similarly as `test library scope`_ is
read from `ROBOT_LIBRARY_SCOPE`. If
`ROBOT_LIBRARY_VERSION` does not exist, information is tried to
be read from `__version__` attribute. These attributes must be
class or module attributes, depending whether the library is
implemented as a class or a module.  For Java libraries the version
attribute must be declared as `static final`.

An example Python module using `__version__`:

.. sourcecode:: python

    __version__ = '0.1'

    def keyword():
        pass

A Java class using `ROBOT_LIBRARY_VERSION`:

.. sourcecode:: java

    public class VersionExample {

        public static final String ROBOT_LIBRARY_VERSION = "1.0.2";

        public void keyword() {
        }
    }

Specifying documentation format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 2.7.5, library documentation tool Libdoc_
supports documentation in multiple formats. If you want to use something
else than Robot Framework's own `documentation formatting`_, you can specify
the format in the source code using  `ROBOT_LIBRARY_DOC_FORMAT` attribute
similarly as scope__ and version__ are set with their own
`ROBOT_LIBRARY_*` attributes.

The possible case-insensitive values for documentation format are
`ROBOT` (default), `HTML`, `TEXT` (plain text),
and `reST` (reStructuredText_). Using the `reST` format requires
the docutils_ module to be installed when documentation is generated.

Setting the documentation format is illustrated by the following Python and
Java examples that use reStructuredText and HTML formats, respectively.
See `Documenting libraries`_ section and Libdoc_ chapter for more information
about documenting test libraries in general.

.. sourcecode:: python

    """A library for *documentation format* demonstration purposes.

    This documentation is created using reStructuredText__. Here is a link
    to the only \`Keyword\`.

    __ http://docutils.sourceforge.net
    """

    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def keyword():
        """**Nothing** to see here. Not even in the table below.

        =======  =====  =====
        Table    here   has
        nothing  to     see.
        =======  =====  =====
        """
        pass

.. sourcecode:: java

    /**
     * A library for <i>documentation format</i> demonstration purposes.
     *
     * This documentation is created using <a href="http://www.w3.org/html">HTML</a>.
     * Here is a link to the only `Keyword`.
     */
    public class DocFormatExample {

        public static final String ROBOT_LIBRARY_DOC_FORMAT = "HTML";

        /**<b>Nothing</b> to see here. Not even in the table below.
         *
         * <table>
         * <tr><td>Table</td><td>here</td><td>has</td></tr>
         * <tr><td>nothing</td><td>to</td><td>see.</td></tr>
         * </table>
         */
        public void keyword() {
        }
    }

__ `Test library scope`_
__ `Specifying library version`_


Library acting as listener
~~~~~~~~~~~~~~~~~~~~~~~~~~

`Listener interface`_ allows external listeners to get notifications about
test execution. They are called, for example, when suites, tests, and keywords
start and end. Sometimes getting such notifications is also useful for test
libraries, and they can register a custom listener by using
`ROBOT_LIBRARY_LISTENER` attribute. The value of this attribute
should be an instance of the listener to use, possibly the library itself.
For more information and examples see `Test libraries as listeners`_ section.

Creating static keywords
------------------------

What methods are considered keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the static library API is used, Robot Framework uses reflection
to find out what public methods the library class or module
implements. It will exclude all methods starting with an underscore,
and with Java libraries also methods that are implemented only in
`java.lang.Object` are ignored. All the methods that are not
ignored are considered keywords. For example, the Python and Java
libraries below implement single keyword :name:`My Keyword`.

.. sourcecode:: python

    class MyLibrary:

        def my_keyword(self, arg):
            return self._helper_method(arg)

        def _helper_method(self, arg):
            return arg.upper()

.. sourcecode:: java

    public class MyLibrary {

        public String myKeyword(String arg) {
            return helperMethod(arg);
        }

        private String helperMethod(String arg) {
            return arg.toUpperCase();
        }
    }

When the library is implemented as a Python module, it is also
possible to limit what methods are keywords by using Python's
`__all__` attribute. If `__all__` is used, only methods
listed in it can be keywords. For example, the library below
implements keywords :name:`Example Keyword` and :name:`Second
Example`. Without `__all__`, it would implement also keywords
:name:`Not Exposed As Keyword` and :name:`Current Thread`. The most
important usage for `__all__` is making sure imported helper
methods, such as `current_thread` in the example below, are not
accidentally exposed as keywords.

.. sourcecode:: python

   from threading import current_thread

   __all__ = ['example_keyword', 'second_example']

   def example_keyword():
       if current_thread().name == 'MainThread':
           print 'Running in main thread'

   def second_example():
       pass

   def not_exposed_as_keyword():
       pass

Keyword names
~~~~~~~~~~~~~

Keyword names used in the test data are compared with method names to
find the method implementing these keywords. Name comparison is
case-insensitive, and also spaces and underscores are ignored. For
example, the method `hello` maps to the keyword name
:name:`Hello`, :name:`hello` or even :name:`h e l l o`. Similarly both the
`do_nothing` and `doNothing` methods can be used as the
:name:`Do Nothing` keyword in the test data.

Example Python library implemented as a module in the :file:`MyLibrary.py` file:

.. sourcecode:: python

  def hello(name):
      print "Hello, %s!" % name

  def do_nothing():
      pass

Example Java library implemented as a class in the :file:`MyLibrary.java` file:

.. sourcecode:: java

  public class MyLibrary {

      public void hello(String name) {
          System.out.println("Hello, " + name + "!");
      }

      public void doNothing() {
      }

  }

The example below illustrates how the example libraries above can be
used. If you want to try this yourself, make sure that the library is
in the `module search path`_.

.. sourcecode:: robotframework

   *** Settings ***
   Library    MyLibrary

   *** Test Cases ***
   My Test
       Do Nothing
       Hello    world

Using a custom keyword name
'''''''''''''''''''''''''''

It is possible to expose a different name for a keyword instead of the
default keyword name which maps to the method name.  This can be accomplished
by setting the `robot_name` attribute on the method to the desired custom name.
The decorator `robot.api.deco.keyword` may be used as a shortcut for setting
this attribute when used as follows:

.. sourcecode:: python

  from robot.api.deco import keyword

  @keyword('Login Via User Panel')
  def login(username, password):
      # ...

.. sourcecode:: robotframework

   *** Test Cases ***
   My Test
       Login Via User Panel    ${username}    ${password}

Using this decorator without an argument will have no effect on the exposed
keyword name, but will still create the `robot_name` attribute.  This can be useful
for `Marking methods to expose as keywords`_ without actually changing
keyword names.

Setting a custom keyword name can also enable library keywords to accept
arguments using `Embedded Arguments`__ syntax.

__ `Embedding arguments into keyword names`_

Keyword tags
~~~~~~~~~~~~

Starting from Robot Framework 2.9, library keywords and `user keywords`__ can
have tags. Library keywords can define them by setting the `robot_tags`
attribute on the method to a list of desired tags. The `robot.api.deco.keyword`
decorator may be used as a shortcut for setting this attribute when used as
follows:

.. sourcecode:: python

  from robot.api.deco import keyword

  @keyword(tags=['tag1', 'tag2'])
  def login(username, password):
      # ...

  @keyword('Custom name', ['tags', 'here'])
  def another_example():
      # ...

Another option for setting tags is giving them on the last line of
`keyword documentation`__ with `Tags:` prefix and separated by a comma. For
example:

.. sourcecode:: python

  def login(username, password):
      """Log user in to SUT.

      Tags: tag1, tag2
      """
      # ...

__ `User keyword tags`_
__ `Documenting libraries`_

Keyword arguments
~~~~~~~~~~~~~~~~~

With a static and hybrid API, the information on how many arguments a
keyword needs is got directly from the method that implements it.
Libraries using the `dynamic library API`_ have other means for sharing
this information, so this section is not relevant to them.

The most common and also the simplest situation is when a keyword needs an
exact number of arguments. In this case, both the Python and Java methods
simply take exactly those arguments. For example, a method implementing a
keyword with no arguments takes no arguments either, a method
implementing a keyword with one argument also takes one argument, and
so on.

Example Python keywords taking different numbers of arguments:

.. sourcecode:: python

  def no_arguments():
      print "Keyword got no arguments."

  def one_argument(arg):
      print "Keyword got one argument '%s'." % arg

  def three_arguments(a1, a2, a3):
      print "Keyword got three arguments '%s', '%s' and '%s'." % (a1, a2, a3)

.. note:: A major limitation with Java libraries using the static library API
          is that they do not support the `named argument syntax`_. If this
          is a blocker, it is possible to either use Python or switch to
          the `dynamic library API`_.

Default values to keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~

It is often useful that some of the arguments that a keyword uses have
default values. Python and Java have different syntax for handling default
values to methods, and the natural syntax of these languages can be
used when creating test libraries for Robot Framework.

Default values with Python
''''''''''''''''''''''''''

In Python a method has always exactly one implementation and possible
default values are specified in the method signature. The syntax,
which is familiar to all Python programmers, is illustrated below:

.. sourcecode:: python

   def one_default(arg='default'):
       print "Argument has value %s" % arg

   def multiple_defaults(arg1, arg2='default 1', arg3='default 2'):
       print "Got arguments %s, %s and %s" % (arg1, arg2, arg3)

The first example keyword above can be used either with zero or one
arguments. If no arguments are given, `arg` gets the value
`default`. If there is one argument, `arg` gets that value,
and calling the keyword with more than one argument fails. In the
second example, one argument is always required, but the second and
the third one have default values, so it is possible to use the keyword
with one to three arguments.

.. sourcecode:: robotframework

   *** Test Cases ***
   Defaults
       One Default
       One Default    argument
       Multiple Defaults    required arg
       Multiple Defaults    required arg    optional
       Multiple Defaults    required arg    optional 1    optional 2

Default values with Java
''''''''''''''''''''''''

In Java one method can have several implementations with different
signatures. Robot Framework regards all these implementations as one
keyword, which can be used with different arguments. This syntax can
thus be used to provide support for the default values. This is
illustrated by the example below, which is functionally identical to
the earlier Python example:

.. sourcecode:: java

   public void oneDefault(String arg) {
       System.out.println("Argument has value " + arg);
   }

   public void oneDefault() {
       oneDefault("default");
   }

   public void multipleDefaults(String arg1, String arg2, String arg3) {
       System.out.println("Got arguments " + arg1 + ", " + arg2 + " and " + arg3);
   }

   public void multipleDefaults(String arg1, String arg2) {
       multipleDefaults(arg1, arg2, "default 2");
   }

   public void multipleDefaults(String arg1) {
       multipleDefaults(arg1, "default 1");
   }

Variable number of arguments (`*varargs`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework supports also keywords that take any number of
arguments. Similarly as with the default values, the actual syntax to use
in test libraries is different in Python and Java.

Variable number of arguments with Python
''''''''''''''''''''''''''''''''''''''''

Python supports methods accepting any number of arguments. The same
syntax works in libraries and, as the examples below show, it can also
be combined with other ways of specifying arguments:

.. sourcecode:: python

  def any_arguments(*args):
      print "Got arguments:"
      for arg in args:
          print arg

  def one_required(required, *others):
      print "Required: %s\nOthers:" % required
      for arg in others:
          print arg

  def also_defaults(req, def1="default 1", def2="default 2", *rest):
      print req, def1, def2, rest

.. sourcecode:: robotframework

   *** Test Cases ***
   Varargs
       Any Arguments
       Any Arguments    argument
       Any Arguments    arg 1    arg 2    arg 3    arg 4    arg 5
       One Required     required arg
       One Required     required arg    another arg    yet another
       Also Defaults    required
       Also Defaults    required    these two    have defaults
       Also Defaults    1    2    3    4    5    6

Variable number of arguments with Java
''''''''''''''''''''''''''''''''''''''

Robot Framework supports `Java varargs syntax`__ for defining variable number of
arguments. For example, the following two keywords are functionally identical
to the above Python examples with same names:

.. sourcecode:: java

  public void anyArguments(String... varargs) {
      System.out.println("Got arguments:");
      for (String arg: varargs) {
          System.out.println(arg);
      }
  }

  public void oneRequired(String required, String... others) {
      System.out.println("Required: " + required + "\nOthers:");
      for (String arg: others) {
          System.out.println(arg);
      }
  }

It is also possible to use variable number of arguments also by
having an array or, starting from Robot Framework 2.8.3,
`java.util.List` as the last argument, or second to last
if `free keyword arguments (**kwargs)`_ are used. This is illustrated
by the following examples that are functionally identical to
the previous ones:

.. sourcecode:: java

  public void anyArguments(String[] varargs) {
      System.out.println("Got arguments:");
      for (String arg: varargs) {
          System.out.println(arg);
      }
  }

  public void oneRequired(String required, List<String> others) {
      System.out.println("Required: " + required + "\nOthers:");
      for (String arg: others) {
          System.out.println(arg);
      }
  }

.. note:: Only `java.util.List` is supported as varargs, not any of
          its sub types.

The support for variable number of arguments with Java keywords has one
limitation: it works only when methods have one signature. Thus it is not
possible to have Java keywords with both default values and varargs.
In addition to that, only Robot Framework 2.8 and newer support using
varargs with `library constructors`__.

__ http://docs.oracle.com/javase/1.5.0/docs/guide/language/varargs.html
__ `Providing arguments to test libraries`_

Free keyword arguments (`**kwargs`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework 2.8 added the support for free keyword arguments using Python's
`**kwargs` syntax. How to use the syntax in the test data is discussed
in `Free keyword arguments`_ section under `Creating test cases`_. In this
section we take a look at how to actually use it in custom test libraries.

Free keyword arguments with Python
''''''''''''''''''''''''''''''''''

If you are already familiar how kwargs work with Python, understanding how
they work with Robot Framework test libraries is rather simple. The example
below shows the basic functionality:

.. sourcecode:: python

    def example_keyword(**stuff):
        for name, value in stuff.items():
            print name, value

.. sourcecode:: robotframework

   *** Test Cases ***
   Keyword Arguments
       Example Keyword    hello=world        # Logs 'hello world'.
       Example Keyword    foo=1    bar=42    # Logs 'foo 1' and 'bar 42'.

Basically, all arguments at the end of the keyword call that use the
`named argument syntax`_ `name=value`, and that do not match any
other arguments, are passed to the keyword as kwargs. To avoid using a literal
value like `foo=quux` as a free keyword argument, it must be escaped__
like `foo\=quux`.

The following example illustrates how normal arguments, varargs, and kwargs
work together:

.. sourcecode:: python

  def various_args(arg, *varargs, **kwargs):
      print 'arg:', arg
      for value in varargs:
          print 'vararg:', value
      for name, value in sorted(kwargs.items()):
          print 'kwarg:', name, value

.. sourcecode:: robotframework

   *** Test Cases ***
   Positional
       Various Args    hello    world                # Logs 'arg: hello' and 'vararg: world'.

   Named
       Various Args    arg=value                     # Logs 'arg: value'.

   Kwargs
       Various Args    a=1    b=2    c=3             # Logs 'kwarg: a 1', 'kwarg: b 2' and 'kwarg: c 3'.
       Various Args    c=3    a=1    b=2             # Same as above. Order does not matter.

   Positional and kwargs
       Various Args    1    2    kw=3                # Logs 'arg: 1', 'vararg: 2' and 'kwarg: kw 3'.

   Named and kwargs
       Various Args    arg=value      hello=world    # Logs 'arg: value' and 'kwarg: hello world'.
       Various Args    hello=world    arg=value      # Same as above. Order does not matter.

For a real world example of using a signature exactly like in the above
example, see :name:`Run Process` and :name:`Start Keyword` keywords in the
Process_ library.

__ Escaping_

Free keyword arguments with Java
''''''''''''''''''''''''''''''''

Starting from Robot Framework 2.8.3, also Java libraries support the free
keyword arguments syntax. Java itself has no kwargs syntax, but keywords
can have `java.util.Map` as the last argument to specify that they
accept kwargs.

If a Java keyword accepts kwargs, Robot Framework will automatically pack
all arguments in `name=value` syntax at the end of the keyword call
into a `Map` and pass it to the keyword. For example, following
example keywords can be used exactly like the previous Python examples:

.. sourcecode:: java

    public void exampleKeyword(Map<String, String> stuff):
        for (String key: stuff.keySet())
            System.out.println(key + " " + stuff.get(key));

    public void variousArgs(String arg, List<String> varargs, Map<String, Object> kwargs):
        System.out.println("arg: " + arg);
        for (String varg: varargs)
            System.out.println("vararg: " + varg);
        for (String key: kwargs.keySet())
            System.out.println("kwarg: " + key + " " + kwargs.get(key));

.. note:: The type of the kwargs argument must be exactly `java.util.Map`,
          not any of its sub types.

.. note:: Similarly as with the `varargs support`__, a keyword supporting
          kwargs cannot have more than one signature.

__ `Variable number of arguments with Java`_

Argument types
~~~~~~~~~~~~~~

Normally keyword arguments come to Robot Framework as strings. If
keywords require some other types, it is possible to either use
variables_ or convert strings to required types inside keywords. With
`Java keywords`__ base types are also coerced automatically.

__ `Argument types with Java`_

Argument types with Python
''''''''''''''''''''''''''

Because arguments in Python do not have any type information, there is
no possibility to automatically convert strings to other types when
using Python libraries. Calling a Python method implementing a keyword
with a correct number of arguments always succeeds, but the execution
fails later if the arguments are incompatible. Luckily with Python it
is simple to convert arguments to suitable types inside keywords:

.. sourcecode:: python

  def connect_to_host(address, port=25):
      port = int(port)
      # ...

Argument types with Java
''''''''''''''''''''''''

Arguments to Java methods have types, and all the base types are
handled automatically. This means that arguments that are normal
strings in the test data are coerced to correct type at runtime. The
types that can be coerced are:

- integer types (`byte`, `short`, `int`, `long`)
- floating point types (`float` and `double`)
- the `boolean` type
- object versions of the above types e.g. `java.lang.Integer`

The coercion is done for arguments that have the same or compatible
type across all the signatures of the keyword method. In the following
example, the conversion can be done for keywords `doubleArgument`
and `compatibleTypes`, but not for `conflictingTypes`.

.. sourcecode:: java

   public void doubleArgument(double arg) {}

   public void compatibleTypes(String arg1, Integer arg2) {}
   public void compatibleTypes(String arg2, Integer arg2, Boolean arg3) {}

   public void conflictingTypes(String arg1, int arg2) {}
   public void conflictingTypes(int arg1, String arg2) {}

The coercion works with the numeric types if the test data has a
string containing a number, and with the boolean type the data must
contain either string `true` or `false`. Coercion is only
done if the original value was a string from the test data, but it is
of course still possible to use variables containing correct types with
these keywords. Using variables is the only option if keywords have
conflicting signatures.

.. sourcecode:: robotframework

   *** Test Cases ***
   Coercion
       Double Argument     3.14
       Double Argument     2e16
       Compatible Types    Hello, world!    1234
       Compatible Types    Hi again!    -10    true

   No Coercion
       Double Argument    ${3.14}
       Conflicting Types    1       ${2}    # must use variables
       Conflicting Types    ${1}    2

Starting from Robot Framework 2.8, argument type coercion works also with
`Java library constructors`__.

__ `Providing arguments to test libraries`_

Using decorators
~~~~~~~~~~~~~~~~

When writing static keywords, it is sometimes useful to modify them with
Python's decorators. However, decorators modify function signatures,
and can confuse Robot Framework's introspection when determining which
arguments keywords accept. This is especially problematic when creating
library documentation with Libdoc_ and when using  RIDE_. To avoid this
issue, either do not use decorators, or use the handy `decorator module`__
to create signature-preserving decorators.

__ http://micheles.googlecode.com/hg/decorator/documentation.html

Embedding arguments into keyword names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Library keywords can also accept arguments which are passed using
`Embedded Argument syntax`__.  The `robot.api.deco.keyword` decorator
can be used to create a `custom keyword name`__ for the keyword
which includes the desired syntax.

__ `Embedding arguments into keyword name`_
__ `Using a custom keyword name`_

.. sourcecode:: python

    from robot.api.deco import keyword

    @keyword('Add ${quantity:\d+} Copies Of ${item} To Cart')
    def add_copies_to_cart(quantity, item):
        # ...

.. sourcecode:: robotframework

   *** Test Cases ***
   My Test
       Add 7 Copies Of Coffee To Cart

Communicating with Robot Framework
----------------------------------

After a method implementing a keyword is called, it can use any
mechanism to communicate with the system under test. It can then also
send messages to Robot Framework's log file, return information that
can be saved to variables and, most importantly, report if the
keyword passed or not.

Reporting keyword status
~~~~~~~~~~~~~~~~~~~~~~~~

Reporting keyword status is done simply using exceptions. If an executed
method raises an exception, the keyword status is `FAIL`, and if it
returns normally, the status is `PASS`.

The error message shown in logs, reports and the console is created
from the exception type and its message. With generic exceptions (for
example, `AssertionError`, `Exception`, and
`RuntimeError`), only the exception message is used, and with
others, the message is created in the format `ExceptionType:
Actual message`.

Starting from Robot Framework 2.8.2, it is possible to avoid adding the
exception type as a prefix to failure message also with non generic exceptions.
This is done by adding a special `ROBOT_SUPPRESS_NAME` attribute with
value `True` to your exception.

Python:

.. sourcecode:: python

    class MyError(RuntimeError):
        ROBOT_SUPPRESS_NAME = True

Java:

.. sourcecode:: java

    public class MyError extends RuntimeException {
        public static final boolean ROBOT_SUPPRESS_NAME = true;
    }

In all cases, it is important for the users that the exception message is as
informative as possible.

HTML in error messages
''''''''''''''''''''''

Starting from Robot Framework 2.8, it is also possible have HTML formatted
error messages by starting the message with text `*HTML*`:

.. sourcecode:: python

   raise AssertionError("*HTML* <a href='robotframework.org'>Robot Framework</a> rulez!!")

This method can be used both when raising an exception in a library, like
in the example above, and `when users provide an error message in the test data`__.

__ `Failures`_

Cutting long messages automatically
'''''''''''''''''''''''''''''''''''

If the error message is longer than 40 lines, it will be automatically
cut from the middle to prevent reports from getting too long and
difficult to read. The full error message is always shown in the log
message of the failed keyword.

Tracebacks
''''''''''

The traceback of the exception is also logged using `DEBUG` `log level`_.
These messages are not visible in log files by default because they are very
rarely interesting for normal users. When developing libraries, it is often a
good idea to run tests using `--loglevel DEBUG`.

Stopping test execution
~~~~~~~~~~~~~~~~~~~~~~~

It is possible to fail a test case so that `the whole test execution is
stopped`__. This is done simply by having a special `ROBOT_EXIT_ON_FAILURE`
attribute with `True` value set on the exception raised from the keyword.
This is illustrated in the examples below.

Python:

.. sourcecode:: python

    class MyFatalError(RuntimeError):
        ROBOT_EXIT_ON_FAILURE = True

Java:

.. sourcecode:: java

    public class MyFatalError extends RuntimeException {
        public static final boolean ROBOT_EXIT_ON_FAILURE = true;
    }

__ `Stopping test execution gracefully`_

Continuing test execution despite of failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to `continue test execution even when there are failures`__.
The way to signal this from test libraries is adding a special
`ROBOT_CONTINUE_ON_FAILURE` attribute with `True` value to the exception
used to communicate the failure. This is demonstrated by the examples below.

Python:

.. sourcecode:: python

    class MyContinuableError(RuntimeError):
        ROBOT_CONTINUE_ON_FAILURE = True

Java:

.. sourcecode:: java

    public class MyContinuableError extends RuntimeException {
        public static final boolean ROBOT_CONTINUE_ON_FAILURE = true;
    }

__ `Continue on failure`_

Logging information
~~~~~~~~~~~~~~~~~~~

Exception messages are not the only way to give information to the
users. In addition to them, methods can also send messages to `log
files`_ simply by writing to the standard output stream (stdout) or to
the standard error stream (stderr), and they can even use different
`log levels`_. Another, and often better, logging possibility is using
the `programmatic logging APIs`_.

By default, everything written by a method into the standard output is
written to the log file as a single entry with the log level
`INFO`. Messages written into the standard error are handled
similarly otherwise, but they are echoed back to the original stderr
after the keyword execution has finished. It is thus possible to use
the stderr if you need some messages to be visible on the console where
tests are executed.

Using log levels
''''''''''''''''

To use other log levels than `INFO`, or to create several
messages, specify the log level explicitly by embedding the level into
the message in the format `*LEVEL* Actual log message`, where
`*LEVEL*` must be in the beginning of a line and `LEVEL` is
one of the available logging levels `TRACE`, `DEBUG`,
`INFO`, `WARN`, `ERROR` and `HTML`.

Errors and warnings
'''''''''''''''''''

Messages with `ERROR` or `WARN` level are automatically written to the
console and a separate `Test Execution Errors section`__ in the log
files. This makes these messages more visible than others and allows
using them for reporting important but non-critical problems to users.

.. note:: In Robot Framework 2.9, new functionality was added to automatically
          add ERRORs logged by keywords to the Test Execution Errors section.

__ `Errors and warnings during execution`_

Logging HTML
''''''''''''

Everything normally logged by the library will be converted into a
format that can be safely represented as HTML. For example,
`<b>foo</b>` will be displayed in the log exactly like that and
not as **foo**. If libraries want to use formatting, links, display
images and so on, they can use a special pseudo log level
`HTML`. Robot Framework will write these messages directly into
the log with the `INFO` level, so they can use any HTML syntax
they want. Notice that this feature needs to be used with care,
because, for example, one badly placed `</table>` tag can ruin
the log file quite badly.

When using the `public logging API`_, various logging methods
have optional `html` attribute that can be set to `True`
to enable logging in HTML format.

Timestamps
''''''''''

By default messages logged via the standard output or error streams
get their timestamps when the executed keyword ends. This means that
the timestamps are not accurate and debugging problems especially with
longer running keywords can be problematic.

Keywords have a possibility to add an accurate timestamp to the messages
they log if there is a need. The timestamp must be given as milliseconds
since the `Unix epoch`__ and it must be placed after the `log level`__
separated from it with a colon::

   *INFO:1308435758660* Message with timestamp
   *HTML:1308435758661* <b>HTML</b> message with timestamp

As illustrated by the examples below, adding the timestamp is easy
both using Python and Java. If you are using Python, it is, however,
even easier to get accurate timestamps using the `programmatic logging
APIs`_. A big benefit of adding timestamps explicitly is that this
approach works also with the `remote library interface`_.

Python:

.. sourcecode:: python

    import time

    def example_keyword():
        print '*INFO:%d* Message with timestamp' % (time.time()*1000)

Java:

.. sourcecode:: java

    public void exampleKeyword() {
        System.out.println("*INFO:" + System.currentTimeMillis() + "* Message with timestamp");
    }

__ http://en.wikipedia.org/wiki/Unix_epoch
__ `Using log levels`_

Logging to console
''''''''''''''''''

If libraries need to write something to the console they have several
options. As already discussed, warnings and all messages written to the
standard error stream are written both to the log file and to the
console. Both of these options have a limitation that the messages end
up to the console only after the currently executing keyword
finishes. A bonus is that these approaches work both with Python and
Java based libraries.

Another option, that is only available with Python, is writing
messages to `sys.__stdout__` or `sys.__stderr__`. When
using this approach, messages are written to the console immediately
and are not written to the log file at all:

.. sourcecode:: python

   import sys

   def my_keyword(arg):
      sys.__stdout__.write('Got arg %s\n' % arg)

The final option is using the `public logging API`_:

.. sourcecode:: python

   from robot.api import logger

   def log_to_console(arg):
      logger.console('Got arg %s' % arg)

   def log_to_console_and_log_file(arg)
      logger.info('Got arg %s' % arg, also_console=True)

Logging example
'''''''''''''''

In most cases, the `INFO` level is adequate. The levels below it,
`DEBUG` and `TRACE`, are useful for writing debug information.
These messages are normally not shown, but they can facilitate debugging
possible problems in the library itself. The `WARN` or `ERROR` level can
be used to make messages more visible and `HTML` is useful if any
kind of formatting is needed.

The following examples clarify how logging with different levels
works. Java programmers should regard the code `print 'message'`
as pseudocode meaning `System.out.println("message");`.

.. sourcecode:: python

   print 'Hello from a library.'
   print '*WARN* Warning from a library.'
   print '*ERROR* Something unexpected happen that may indicate a problem in the test.'
   print '*INFO* Hello again!'
   print 'This will be part of the previous message.'
   print '*INFO* This is a new message.'
   print '*INFO* This is <b>normal text</b>.'
   print '*HTML* This is <b>bold</b>.'
   print '*HTML* <a href="http://robotframework.org">Robot Framework</a>'

.. raw:: html

   <table class="messages">
     <tr>
       <td class="time">16:18:42.123</td>
       <td class="info level">INFO</td>
       <td class="msg">Hello from a library.</td>
     </tr>
     <tr>
       <td class="time">16:18:42.123</td>
       <td class="warn level">WARN</td>
       <td class="msg">Warning from a library.</td>
     </tr>
     <tr>
       <td class="time">16:18:42.123</td>
       <td class="error level">ERROR</td>
       <td class="msg">Something unexpected happen that may indicate a problem in the test.</td>
     </tr>
     <tr>
       <td class="time">16:18:42.123</td>
       <td class="info level">INFO</td>
       <td class="msg">Hello again!<br>This will be part of the previous message.</td>
     </tr>
     <tr>
       <td class="time">16:18:42.123</td>
       <td class="info level">INFO</td>
       <td class="msg">This is a new message.</td>
     </tr>
     <tr>
       <td class="time">16:18:42.123</td>
       <td class="info level">INFO</td>
       <td class="msg">This is &lt;b&gt;normal text&lt;/b&gt;.</td>
     </tr>
     <tr>
       <td class="time">16:18:42.123</td>
       <td class="info level">INFO</td>
       <td class="msg">This is <b>bold</b>.</td>
     </tr>
     <tr>
       <td class="time">16:18:42.123</td>
       <td class="info level">INFO</td>
       <td class="msg"><a href="http://robotframework.org">Robot Framework</a></td>
     </tr>
   </table>

Programmatic logging APIs
~~~~~~~~~~~~~~~~~~~~~~~~~

Programmatic APIs provide somewhat cleaner way to log information than
using the standard output and error streams. Currently these
interfaces are available only to Python bases test libraries.

Public logging API
''''''''''''''''''

Robot Framework has a Python based logging API for writing
messages to the log file and to the console. Test libraries can use
this API like `logger.info('My message')` instead of logging
through the standard output like `print '*INFO* My message'`. In
addition to a programmatic interface being a lot cleaner to use, this
API has a benefit that the log messages have accurate timestamps_.

The public logging API `is thoroughly documented`__ as part of the API
documentation at https://robot-framework.readthedocs.org. Below is
a simple usage example:

.. sourcecode:: python

   from robot.api import logger

   def my_keyword(arg):
       logger.debug('Got argument %s' % arg)
       do_something()
       logger.info('<i>This</i> is a boring example', html=True)
       logger.console('Hello, console!')

An obvious limitation is that test libraries using this logging API have
a dependency to Robot Framework. Before version 2.8.7 Robot also had
to be running for the logging to work. Starting from Robot Framework 2.8.7
if Robot is not running the messages are redirected automatically to Python's
standard logging__ module.

__ https://robot-framework.readthedocs.org/en/latest/autodoc/robot.api.html#module-robot.api.logger
__ http://docs.python.org/library/logging.html

Using Python's standard `logging` module
''''''''''''''''''''''''''''''''''''''''

In addition to the new `public logging API`_, Robot Framework offers a
built-in support to Python's standard logging__ module. This
works so that all messages that are received by the root logger of the
module are automatically propagated to Robot Framework's log
file. Also this API produces log messages with accurate timestamps_,
but logging HTML messages or writing messages to the console are not
supported. A big benefit, illustrated also by the simple example
below, is that using this logging API creates no dependency to Robot
Framework.

.. sourcecode:: python

   import logging

   def my_keyword(arg):
       logging.debug('Got argument %s' % arg)
       do_something()
       logging.info('This is a boring example')

The `logging` module has slightly different log levels than
Robot Framework. Its levels `DEBUG`, `INFO`, `WARNING` and `ERROR` are mapped
directly to the matching Robot Framework log levels, and `CRITICAL`
is mapped to `ERROR`. Custom log levels are mapped to the closest
standard level smaller than the custom level. For example, a level
between `INFO` and `WARNING` is mapped to Robot Framework's `INFO` level.

__ http://docs.python.org/library/logging.html

Logging during library initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Libraries can also log during the test library import and initialization.
These messages do not appear in the `log file`_ like the normal log messages,
but are instead written to the `syslog`_. This allows logging any kind of
useful debug information about the library initialization. Messages logged
using the `WARN` or `ERROR` levels are also visible in the `test execution errors`_
section in the log file.

Logging during the import and initialization is possible both using the
`standard output and error streams`__ and the `programmatic logging APIs`_.
Both of these are demonstrated below.

Java library logging via stdout during initialization:

.. sourcecode:: java

   public class LoggingDuringInitialization {

       public LoggingDuringInitialization() {
           System.out.println("*INFO* Initializing library");
       }

       public void keyword() {
           // ...
       }
   }

Python library logging using the logging API during import:

.. sourcecode:: python

   from robot.api import logger

   logger.debug("Importing library")

   def keyword():
       # ...

.. note:: If you log something during initialization, i.e. in Python
          `__init__` or in Java constructor, the messages may be
          logged multiple times depending on the `test library scope`_.

__ `Logging information`_

Returning values
~~~~~~~~~~~~~~~~

The final way for keywords to communicate back to the core framework
is returning information retrieved from the system under test or
generated by some other means. The returned values can be `assigned to
variables`__ in the test data and then used as inputs for other keywords,
even from different test libraries.

Values are returned using the `return` statement both from
the Python and Java methods. Normally, one value is assigned into one
`scalar variable`__, as illustrated in the example below. This example
also illustrates that it is possible to return any objects and to use
`extended variable syntax`_ to access object attributes.

__ `Return values from keywords`_
__ `Scalar variables`_

.. sourcecode:: python

  from mymodule import MyObject

  def return_string():
      return "Hello, world!"

  def return_object(name):
      return MyObject(name)

.. sourcecode:: robotframework

   *** Test Cases ***
   Returning one value
       ${string} =    Return String
       Should Be Equal    ${string}    Hello, world!
       ${object} =    Return Object    Robot
       Should Be Equal    ${object.name}    Robot

Keywords can also return values so that they can be assigned into
several `scalar variables`_ at once, into `a list variable`__, or
into scalar variables and a list variable. All these usages require
that returned values are Python lists or tuples or
in Java arrays, Lists, or Iterators.

__ `List variables`_

.. sourcecode:: python

  def return_two_values():
      return 'first value', 'second value'

  def return_multiple_values():
      return ['a', 'list', 'of', 'strings']


.. sourcecode:: robotframework

   *** Test Cases ***
   Returning multiple values
       ${var1}    ${var2} =    Return Two Values
       Should Be Equal    ${var1}    first value
       Should Be Equal    ${var2}    second value
       @{list} =    Return Two Values
       Should Be Equal    @{list}[0]    first value
       Should Be Equal    @{list}[1]    second value
       ${s1}    ${s2}    @{li} =    Return Multiple Values
       Should Be Equal    ${s1} ${s2}    a list
       Should Be Equal    @{li}[0] @{li}[1]    of strings

Communication when using threads
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a library uses threads, it should generally communicate with the
framework only from the main thread. If a worker thread has, for
example, a failure to report or something to log, it should pass the
information first to the main thread, which can then use exceptions or
other mechanisms explained in this section for communication with the
framework.

This is especially important when threads are run on background while
other keywords are running. Results of communicating with the
framework in that case are undefined and can in the worst case cause a
crash or a corrupted output file. If a keyword starts something on
background, there should be another keyword that checks the status of
the worker thread and reports gathered information accordingly.

Messages logged by non-main threads using the normal logging methods from
`programmatic logging APIs`_  are silently ignored.

There is also a `BackgroundLogger` in separate robotbackgroundlogger__ project,
with a similar API as the standard `robot.api.logger`. Normal logging
methods will ignore messages from other than main thread, but the
`BackgroundLogger` will save the background messages so that they can be later
logged to Robot's log.

__ https://github.com/robotframework/robotbackgroundlogger

Distributing test libraries
---------------------------

Documenting libraries
~~~~~~~~~~~~~~~~~~~~~

A test library without documentation about what keywords it
contains and what those keywords do is rather useless. To ease
maintenance, it is highly recommended that library documentation is
included in the source code and generated from it. Basically, that
means using docstrings_ with Python and Javadoc_ with Java, as in
the examples below.

.. sourcecode:: python

    class MyLibrary:
        """This is an example library with some documentation."""

        def keyword_with_short_documentation(self, argument):
            """This keyword has only a short documentation"""
            pass

        def keyword_with_longer_documentation(self):
            """First line of the documentation is here.

            Longer documentation continues here and it can contain
            multiple lines or paragraphs.
            """
            pass

.. sourcecode:: java

    /**
     *  This is an example library with some documentation.
     */
    public class MyLibrary {

        /**
         * This keyword has only a short documentation
         */
        public void keywordWithShortDocumentation(String argument) {
        }

        /**
         * First line of the documentation is here.
         *
         * Longer documentation continues here and it can contain
         * multiple lines or paragraphs.
         */
        public void keywordWithLongerDocumentation() {
        }

    }

Both Python and Java have tools for creating an API documentation of a
library documented as above. However, outputs from these tools can be slightly
technical for some users. Another alternative is using Robot
Framework's own documentation tool Libdoc_. This tool can
create a library documentation from both Python and Java libraries
using the static library API, such as the ones above, but it also handles
libraries using the `dynamic library API`_ and `hybrid library API`_.

The first line of a keyword documentation is used for a special
purpose and should contain a short overall description of the
keyword. It is used as a *short documentation*, for example as a tool
tip, by Libdoc_ and also shown in the test logs. However, the latter
does not work with Java libraries using the static API,
because their documentations are lost in compilation and not available
at runtime.

By default documentation is considered to follow Robot Framework's
`documentation formatting`_ rules. This simple format allows often used
styles like `*bold*` and `_italic_`, tables, lists, links, etc.
Starting from Robot Framework 2.7.5, it is possible to use also HTML, plain
text and reStructuredText_ formats. See `Specifying documentation format`_
section for information how to set the format in the library source code and
Libdoc_ chapter for more information about the formats in general.

.. note:: If you want to use non-ASCII characters in the documentation of
          Python libraries, you must either use UTF-8 as your `source code
          encoding`__ or create docstrings as Unicode.

.. _docstrings: http://www.python.org/dev/peps/pep-0257
.. _javadoc: http://java.sun.com/j2se/javadoc/writingdoccomments/index.html
__ http://www.python.org/dev/peps/pep-0263

Testing libraries
~~~~~~~~~~~~~~~~~

Any non-trivial test library needs to be thoroughly tested to prevent
bugs in them. Of course, this testing should be automated to make it
easy to rerun tests when libraries are changed.

Both Python and Java have excellent unit testing tools, and they suite
very well for testing libraries. There are no major differences in
using them for this purpose compared to using them for some other
testing. The developers familiar with these tools do not need to learn
anything new, and the developers not familiar with them should learn
them anyway.

It is also easy to use Robot Framework itself for testing libraries
and that way have actual end-to-end acceptance tests for them. There are
plenty of useful keywords in the BuiltIn_ library for this
purpose. One worth mentioning specifically is :name:`Run Keyword And Expect
Error`, which is useful for testing that keywords report errors
correctly.

Whether to use a unit- or acceptance-level testing approach depends on
the context. If there is a need to simulate the actual system under
test, it is often easier on the unit level. On the other hand,
acceptance tests ensure that keywords do work through Robot
Framework. If you cannot decide, of course it is possible to use both
the approaches.

Packaging libraries
~~~~~~~~~~~~~~~~~~~

After a library is implemented, documented, and tested, it still needs
to be distributed to the users. With simple libraries consisting of a
single file, it is often enough to ask the users to copy that file
somewhere and set the `module search path`_ accordingly. More
complicated libraries should be packaged to make the installation
easier.

Since libraries are normal programming code, they can be packaged
using normal packaging tools. With Python, good options include
distutils_, contained by Python's standard library, and the newer
setuptools_. A benefit of these tools is that library modules are
installed into a location that is automatically in the `module
search path`_.

When using Java, it is natural to package libraries into a JAR
archive. The JAR package must be put into the `module search path`_
before running tests, but it is easy to create a `start-up script`_ that
does that automatically.

Deprecating keywords
~~~~~~~~~~~~~~~~~~~~

Sometimes there is a need to replace existing keywords with new ones
or remove them altogether. Just informing the users about the change
may not always be enough, and it is more efficient to get warnings at
runtime. To support that, Robot Framework has a capability to mark
keywords *deprecated*. This makes it easier to find old keywords from
the test data and remove or replace them.

Keywords can be deprecated by starting their documentation with text
`*DEPRECATED`, case-sensitive, and having a closing `*` also on the first
line of the documentation. For example, `*DEPRECATED*`, `*DEPRECATED.*`, and
`*DEPRECATED in version 1.5.*` are all valid markers.

When a deprecated keyword is executed, a deprecation warning is logged and
the warning is shown also in `the console and the Test Execution Errors
section in log files`__. The deprecation warning starts with text `Keyword
'<name>' is deprecated.` and has rest of the `short documentation`__ after
the deprecation marker, if any, afterwards. For example, if the following
keyword is executed, there will be a warning like shown below in the log file.

.. sourcecode:: python

    def example_keyword(argument):
        """*DEPRECATED!!* Use keyword `Other Keyword` instead.

        This keyword does something to given ``argument`` and returns results.
        """
        return do_something(argument)

.. raw:: html

   <table class="messages">
     <tr>
       <td class="time">20080911&nbsp;16:00:22.650</td>
       <td class="warn level">WARN</td>
       <td class="msg">Keyword 'SomeLibrary.Example Keyword' is deprecated. Use keyword `Other Keyword` instead.</td>
     </tr>
   </table>

This deprecation system works with most test libraries and also with
`user keywords`__.  The only exception are keywords implemented in a
Java test library that uses the `static library interface`__ because
their documentation is not available at runtime. With such keywords,
it possible to use user keywords as wrappers and deprecate them.

.. note:: Prior to Robot Framework 2.9 the documentation must start with
          `*DEPRECATED*` exactly without any extra content before the
          closing `*`.

__ `Errors and warnings during execution`_
__ `Documenting libraries`_
__ `User keyword name and documentation`_
__ `Creating static keywords`_

.. _Dynamic library:

Dynamic library API
-------------------

The dynamic API is in most ways similar to the static API. For
example, reporting the keyword status, logging, and returning values
works exactly the same way. Most importantly, there are no differences
in importing dynamic libraries and using their keywords compared to
other libraries. In other words, users do not need to know what APIs their
libraries use.

Only differences between static and dynamic libraries are
how Robot Framework discovers what keywords a library implements,
what arguments and documentation these keywords have, and how the
keywords are actually executed. With the static API, all this is
done using reflection (except for the documentation of Java libraries),
but dynamic libraries have special methods that are used for these
purposes.

One of the benefits of the dynamic API is that you have more flexibility
in organizing your library. With the static API, you must have all
keywords in one class or module, whereas with the dynamic API, you can,
for example, implement each keyword as a separate class. This use case is
not so important with Python, though, because its dynamic capabilities and
multi-inheritance already give plenty of flexibility, and there is also
possibility to use the `hybrid library API`_.

Another major use case for the dynamic API is implementing a library
so that it works as proxy for an actual library possibly running on
some other process or even on another machine. This kind of a proxy
library can be very thin, and because keyword names and all other
information is got dynamically, there is no need to update the proxy
when new keywords are added to the actual library.

This section explains how the dynamic API works between Robot
Framework and dynamic libraries. It does not matter for Robot
Framework how these libraries are actually implemented (for example,
how calls to the `run_keyword` method are mapped to a correct
keyword implementation), and many different approaches are
possible. However, if you use Java, you may want to examine
`JavalibCore <https://github.com/robotframework/JavalibCore>`__
before implementing your own system. This collection of
reusable tools supports several ways of creating keywords, and it is
likely that it already has a mechanism that suites your needs.

.. _`Getting dynamic keyword names`:

Getting keyword names
~~~~~~~~~~~~~~~~~~~~~

Dynamic libraries tell what keywords they implement with the
`get_keyword_names` method. The method also has the alias
`getKeywordNames` that is recommended when using Java. This
method cannot take any arguments, and it must return a list or array
of strings containing the names of the keywords that the library implements.

If the returned keyword names contain several words, they can be returned
separated with spaces or underscores, or in the camelCase format. For
example, `['first keyword', 'second keyword']`,
`['first_keyword', 'second_keyword']`, and
`['firstKeyword', 'secondKeyword']` would all be mapped to keywords
:name:`First Keyword` and :name:`Second Keyword`.

Dynamic libraries must always have this method. If it is missing, or
if calling it fails for some reason, the library is considered a
static library.

Marking methods to expose as keywords
'''''''''''''''''''''''''''''''''''''

If a dynamic library should contain both methods which are meant to be keywords
and methods which are meant to be private helper methods, it may be wise to
mark the keyword methods as such so it is easier to implement `get_keyword_names`.
The `robot.api.deco.keyword` decorator allows an easy way to do this since it
creates a custom `robot_name` attribute on the decorated method.
This allows generating the list of keywords just by checking for the `robot_name`
attribute on every method in the library during `get_keyword_names`.  See
`Using a custom keyword name`_ for more about this decorator.

.. sourcecode:: python

   from robot.api.deco import keyword

   class DynamicExample:

       def get_keyword_names(self):
           return [name for name in dir(self) if hasattr(getattr(self, name), 'robot_name')]

       def helper_method(self):
           # ...

       @keyword
       def keyword_method(self):
           # ...

.. _`Running dynamic keywords`:

Running keywords
~~~~~~~~~~~~~~~~

Dynamic libraries have a special `run_keyword` (alias
`runKeyword`) method for executing their keywords. When a
keyword from a dynamic library is used in the test data, Robot
Framework uses the library's `run_keyword` method to get it
executed. This method takes two or three arguments. The first argument is a
string containing the name of the keyword to be executed in the same
format as returned by `get_keyword_names`. The second argument is
a list or array of arguments given to the keyword in the test data.

The optional third argument is a dictionary (map in Java) that gets
possible `free keyword arguments`_ (`**kwargs`) passed to the
keyword. See `free keyword arguments with dynamic libraries`_ section
for more details about using kwargs with dynamic test libraries.

After getting keyword name and arguments, the library can execute
the keyword freely, but it must use the same mechanism to
communicate with the framework as static libraries. This means using
exceptions for reporting keyword status, logging by writing to
the standard output or by using provided logging APIs, and using
the return statement in `run_keyword` for returning something.

Every dynamic library must have both the `get_keyword_names` and
`run_keyword` methods but rest of the methods in the dynamic
API are optional. The example below shows a working, albeit
trivial, dynamic library implemented in Python.

.. sourcecode:: python

   class DynamicExample:

       def get_keyword_names(self):
           return ['first keyword', 'second keyword']

       def run_keyword(self, name, args):
           print "Running keyword '%s' with arguments %s." % (name, args)

Getting keyword arguments
~~~~~~~~~~~~~~~~~~~~~~~~~

If a dynamic library only implements the `get_keyword_names` and
`run_keyword` methods, Robot Framework does not have any information
about the arguments that the implemented keywords need. For example,
both :name:`First Keyword` and :name:`Second Keyword` in the example above
could be used with any number of arguments. This is problematic,
because most real keywords expect a certain number of keywords, and
under these circumstances they would need to check the argument counts
themselves.

Dynamic libraries can tell Robot Framework what arguments the keywords
it implements expect by using the `get_keyword_arguments`
(alias `getKeywordArguments`) method. This method takes the name
of a keyword as an argument, and returns a list or array of strings
containing the arguments accepted by that keyword.

Similarly as static keywords, dynamic keywords can require any number
of arguments, have default values, and accept variable number of
arguments and free keyword arguments. The syntax for how to represent
all these different variables is explained in the following table.
Note that the examples use Python syntax for lists, but Java developers
should use Java lists or String arrays instead.

.. table:: Representing different arguments with `get_keyword_arguments`
   :class: tabular

   +--------------------+----------------------------+------------------------------+----------+
   |    Expected        |      How to represent      |            Examples          | Limits   |
   |    arguments       |                            |                              | (min/max)|
   +====================+============================+==============================+==========+
   | No arguments       | Empty list.                | | `[]`                       | | 0/0    |
   +--------------------+----------------------------+------------------------------+----------+
   | One or more        | List of strings containing | | `['one_argument']`         | | 1/1    |
   | argument           | argument names.            | | `['a1', 'a2', 'a3']`       | | 3/3    |
   +--------------------+----------------------------+------------------------------+----------+
   | Default values     | Default values separated   | | `['arg=default value']`    | | 0/1    |
   | for arguments      | from names with `=`.       | | `['a', 'b=1', 'c=2']`      | | 1/3    |
   |                    | Default values are always  |                              |          |
   |                    | considered to be strings.  |                              |          |
   +--------------------+----------------------------+------------------------------+----------+
   | Variable number    | Last (or second last with  | | `['*varargs']`             | | 0/any  |
   | of arguments       | kwargs) argument has `*`   | | `['a', 'b=42', '*rest']`   | | 1/any  |
   | (varargs)          | before its name.           |                              |          |
   +--------------------+----------------------------+------------------------------+----------+
   | Free keyword       | Last arguments has         | | `['**kwargs']`             | | 0/0    |
   | arguments (kwargs) | `**` before its name.      | | `['a', 'b=42', '**kws']`   | | 1/2    |
   |                    |                            | | `['*varargs', '**kwargs']` | | 0/any  |
   +--------------------+----------------------------+------------------------------+----------+

When the `get_keyword_arguments` is used, Robot Framework automatically
calculates how many positional arguments the keyword requires and does it
support free keyword arguments or not. If a keyword is used with invalid
arguments, an error occurs and `run_keyword` is not even called.

The actual argument names and default values that are returned are also
important. They are needed for `named argument support`__ and the Libdoc_
tool needs them to be able to create a meaningful library documentation.

If `get_keyword_arguments` is missing or returns `None` or
`null` for a certain keyword, that keyword gets an argument specification
accepting all arguments. This automatic argument spec is either
`[*varargs, **kwargs]` or `[*varargs]`, depending does
`run_keyword` `support kwargs`__ by having three arguments or not.

__ `Named argument syntax with dynamic libraries`_
__ `Free keyword arguments with dynamic libraries`_

Getting keyword documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The final special method that dynamic libraries can implement is
`get_keyword_documentation` (alias
`getKeywordDocumentation`). It takes a keyword name as an
argument and, as the method name implies, returns its documentation as
a string.

The returned documentation is used similarly as the keyword
documentation string with static libraries implemented with
Python. The main use case is getting keywords' documentations into a
library documentation generated by Libdoc_. Additionally,
the first line of the documentation (until the first `\n`) is
shown in test logs.

Getting keyword tags
~~~~~~~~~~~~~~~~~~~~

Dynamic libraries do not have any other way for defining `keyword tags`_
than by specifying them on the last row of the documentation with `Tags:`
prefix. Separate `get_keyword_tags` method can be added to the dynamic API
later if there is a need.

Getting general library documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `get_keyword_documentation` method can also be used for
specifying overall library documentation. This documentation is not
used when tests are executed, but it can make the documentation
generated by Libdoc_ much better.

Dynamic libraries can provide both general library documentation and
documentation related to taking the library into use. The former is
got by calling `get_keyword_documentation` with special value
`__intro__`, and the latter is got using value
`__init__`. How the documentation is presented is best tested
with Libdoc_ in practice.

Python based dynamic libraries can also specify the general library
documentation directly in the code as the docstring of the library
class and its `__init__` method. If a non-empty documentation is
got both directly from the code and from the
`get_keyword_documentation` method, the latter has precedence.

Named argument syntax with dynamic libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 2.8, also the dynamic library API supports
the `named argument syntax`_. Using the syntax works based on the
argument names and default values `got from the library`__ using the
`get_keyword_arguments` method.

For the most parts, the named arguments syntax works with dynamic keywords
exactly like it works with any other keyword supporting it. The only special
case is the situation where a keyword has multiple arguments with default
values, and only some of the latter ones are given. In that case the framework
fills the skipped optional arguments based on the default values returned
by the `get_keyword_arguments` method.

Using the named argument syntax with dynamic libraries is illustrated
by the following examples. All the examples use a keyword :name:`Dynamic`
that has been specified to have argument specification
`[arg1, arg2=xxx, arg3=yyy]`.
The comment shows the arguments that the keyword is actually called with.

.. sourcecode:: robotframework

   *** Test Cases ***
   Only positional
       Dynamic    a                             # [a]
       Dynamic    a         b                   # [a, b]
       Dynamic    a         b         c         # [a, b, c]

   Named
       Dynamic    a         arg2=b              # [a, b]
       Dynamic    a         b         arg3=c    # [a, b, c]
       Dynamic    a         arg2=b    arg3=c    # [a, b, c]
       Dynamic    arg1=a    arg2=b    arg3=c    # [a, b, c]

   Fill skipped
       Dynamic    a         arg3=c              # [a, xxx, c]

__ `Getting keyword arguments`_

Free keyword arguments with dynamic libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 2.8.2, dynamic libraries can also support
`free keyword arguments`_ (`**kwargs`). A mandatory precondition for
this support is that the `run_keyword` method `takes three arguments`__:
the third one will get kwargs when they are used. Kwargs are passed to the
keyword as a dictionary (Python) or Map (Java).

What arguments a keyword accepts depends on what `get_keyword_arguments`
`returns for it`__. If the last argument starts with `**`, that keyword is
recognized to accept kwargs.

Using the free keyword argument syntax with dynamic libraries is illustrated
by the following examples. All the examples use a keyword :name:`Dynamic`
that has been specified to have argument specification
`[arg1=xxx, arg2=yyy, **kwargs]`.
The comment shows the arguments that the keyword is actually called with.

.. sourcecode:: robotframework

   *** Test Cases ***
   No arguments
       Dynamic                            # [], {}

   Only positional
       Dynamic    a                       # [a], {}
       Dynamic    a         b             # [a, b], {}

   Only kwargs
       Dynamic    a=1                     # [], {a: 1}
       Dynamic    a=1       b=2    c=3    # [], {a: 1, b: 2, c: 3}

   Positional and kwargs
       Dynamic    a         b=2           # [a], {b: 2}
       Dynamic    a         b=2    c=3    # [a], {b: 2, c: 3}

   Named and kwargs
       Dynamic    arg1=a    b=2           # [a], {b: 2}
       Dynamic    arg2=a    b=2    c=3    # [xxx, a], {b: 2, c: 3}

__ `Running dynamic keywords`_
__ `Getting keyword arguments`_

Summary
~~~~~~~

All special methods in the dynamic API are listed in the table
below. Method names are listed in the underscore format, but their
camelCase aliases work exactly the same way.

.. table:: All special methods in the dynamic API
   :class: tabular

   ===========================  =========================  =======================================================
               Name                    Arguments                                  Purpose
   ===========================  =========================  =======================================================
   `get_keyword_names`                                     `Return names`__ of the implemented keywords.
   `run_keyword`                `name, arguments, kwargs`  `Execute the specified keyword`__ with given arguments. `kwargs` is optional.
   `get_keyword_arguments`      `name`                     Return keywords' `argument specifications`__. Optional method.
   `get_keyword_documentation`  `name`                     Return keywords' and library's `documentation`__. Optional method.
   ===========================  =========================  =======================================================

__ `Getting dynamic keyword names`_
__ `Running dynamic keywords`_
__ `Getting keyword arguments`_
__ `Getting keyword documentation`_

It is possible to write a formal interface specification in Java as
below. However, remember that libraries *do not need* to implement
any explicit interface, because Robot Framework directly checks with
reflection if the library has the required `get_keyword_names` and
`run_keyword` methods or their camelCase aliases. Additionally,
`get_keyword_arguments` and `get_keyword_documentation`
are completely optional.

.. sourcecode:: java

   public interface RobotFrameworkDynamicAPI {

       List<String> getKeywordNames();

       Object runKeyword(String name, List arguments);

       Object runKeyword(String name, List arguments, Map kwargs);

       List<String> getKeywordArguments(String name);

       String getKeywordDocumentation(String name);

   }

.. note:: In addition to using `List`, it is possible to use also arrays
          like `Object[]` or `String[]`.

A good example of using the dynamic API is Robot Framework's own
`Remote library`_.

Hybrid library API
------------------

The hybrid library API is, as its name implies, a hybrid between the
static API and the dynamic API. Just as with the dynamic API, it is
possible to implement a library using the hybrid API only as a class.

Getting keyword names
~~~~~~~~~~~~~~~~~~~~~

Keyword names are got in the exactly same way as with the dynamic
API. In practice, the library needs to have the
`get_keyword_names` or `getKeywordNames` method returning
a list of keyword names that the library implements.

Running keywords
~~~~~~~~~~~~~~~~

In the hybrid API, there is no `run_keyword` method for executing
keywords. Instead, Robot Framework uses reflection to find methods
implementing keywords, similarly as with the static API. A library
using the hybrid API can either have those methods implemented
directly or, more importantly, it can handle them dynamically.

In Python, it is easy to handle missing methods dynamically with the
`__getattr__` method. This special method is probably familiar
to most Python programmers and they can immediately understand the
following example. Others may find it easier to consult `Python Reference
Manual`__ first.

__ http://docs.python.org/reference/datamodel.html#attribute-access

.. sourcecode:: python

   from somewhere import external_keyword

   class HybridExample:

       def get_keyword_names(self):
           return ['my_keyword', 'external_keyword']

       def my_keyword(self, arg):
           print "My Keyword called with '%s'" % arg

       def __getattr__(self, name):
           if name == 'external_keyword':
               return external_keyword
           raise AttributeError("Non-existing attribute '%s'" % name)

Note that `__getattr__` does not execute the actual keyword like
`run_keyword` does with the dynamic API. Instead, it only
returns a callable object that is then executed by Robot Framework.

Another point to be noted is that Robot Framework uses the same names that
are returned from `get_keyword_names` for finding the methods
implementing them. Thus the names of the methods that are implemented in
the class itself must be returned in the same format as they are
defined. For example, the library above would not work correctly, if
`get_keyword_names` returned `My Keyword` instead of
`my_keyword`.

The hybrid API is not very useful with Java, because it is not
possible to handle missing methods with it. Of course, it is possible
to implement all the methods in the library class, but that brings few
benefits compared to the static API.

Getting keyword arguments and documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When this API is used, Robot Framework uses reflection to find the
methods implementing keywords, similarly as with the static API. After
getting a reference to the method, it searches for arguments and
documentation from it, in the same way as when using the static
API. Thus there is no need for special methods for getting arguments
and documentation like there is with the dynamic API.

Summary
~~~~~~~

When implementing a test library in Python, the hybrid API has the same
dynamic capabilities as the actual dynamic API. A great benefit with it is
that there is no need to have special methods for getting keyword
arguments and documentation. It is also often practical that the only real
dynamic keywords need to be handled in `__getattr__` and others
can be implemented directly in the main library class.

Because of the clear benefits and equal capabilities, the hybrid API
is in most cases a better alternative than the dynamic API when using
Python. One notable exception is implementing a library as a proxy for
an actual library implementation elsewhere, because then the actual
keyword must be executed elsewhere and the proxy can only pass forward
the keyword name and arguments.

A good example of using the hybrid API is Robot Framework's own
Telnet_ library.

Using Robot Framework's internal modules
----------------------------------------

Test libraries implemented with Python can use Robot Framework's
internal modules, for example, to get information about the executed
tests and the settings that are used. This powerful mechanism to
communicate with the framework should be used with care, though,
because all Robot Framework's APIs are not meant to be used by
externally and they might change radically between different framework
versions.

Available APIs
~~~~~~~~~~~~~~

Starting from Robot Framework 2.7, `API documentation`_ is hosted separately
at the excellent `Read the Docs`_ service. If you are unsure how to use
certain API or is using them forward compatible, please send a question
to `mailing list`_.

Using BuiltIn library
~~~~~~~~~~~~~~~~~~~~~

The safest API to use are methods implementing keywords in the
BuiltIn_ library. Changes to keywords are rare and they are always
done so that old usage is first deprecated. One of the most useful
methods is `replace_variables` which allows accessing currently
available variables. The following example demonstrates how to get
`${OUTPUT_DIR}` which is one of the many handy `automatic
variables`_. It is also possible to set new variables from libraries
using `set_test_variable`, `set_suite_variable` and
`set_global_variable`.

.. sourcecode:: python

   import os.path
   from robot.libraries.BuiltIn import BuiltIn

   def do_something(argument):
       output = do_something_that_creates_a_lot_of_output(argument)
       outputdir = BuiltIn().replace_variables('${OUTPUTDIR}')
       path = os.path.join(outputdir, 'results.txt')
       f = open(path, 'w')
       f.write(output)
       f.close()
       print '*HTML* Output written to <a href="results.txt">results.txt</a>'

The only catch with using methods from `BuiltIn` is that all
`run_keyword` method variants must be handled specially.
Methods that use `run_keyword` methods have to be registered
as *run keywords* themselves using `register_run_keyword`
method in `BuiltIn` module. This method's documentation explains
why this needs to be done and obviously also how to do it.

Extending existing test libraries
---------------------------------

This section explains different approaches how to add new
functionality to existing test libraries and how to use them in your
own libraries otherwise.

Modifying original source code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have access to the source code of the library you want to
extend, you can naturally modify the source code directly. The biggest
problem of this approach is that it can be hard for you to update the
original library without affecting your changes. For users it may also
be confusing to use a library that has different functionality than
the original one. Repackaging the library may also be a big extra
task.

This approach works extremely well if the enhancements are generic and
you plan to submit them back to the original developers. If your
changes are applied to the original library, they are included in the
future releases and all the problems discussed above are mitigated. If
changes are non-generic, or you for some other reason cannot submit
them back, the approaches explained in the subsequent sections
probably work better.

Using inheritance
~~~~~~~~~~~~~~~~~

Another straightforward way to extend an existing library is using
inheritance. This is illustrated by the example below that adds new
:name:`Title Should Start With` keyword to the SeleniumLibrary_. This
example uses Python, but you can obviously extend an existing Java
library in Java code the same way.

.. sourcecode:: python

   from SeleniumLibrary import SeleniumLibrary

   class ExtendedSeleniumLibrary(SeleniumLibrary):

       def title_should_start_with(self, expected):
           title = self.get_title()
           if not title.startswith(expected):
               raise AssertionError("Title '%s' did not start with '%s'"
                                    % (title, expected))

A big difference with this approach compared to modifying the original
library is that the new library has a different name than the
original. A benefit is that you can easily tell that you are using a
custom library, but a big problem is that you cannot easily use the
new library with the original. First of all your new library will have
same keywords as the original meaning that there is always
conflict__. Another problem is that the libraries do not share their
state.

This approach works well when you start to use a new library and want
to add custom enhancements to it from the beginning. Otherwise other
mechanisms explained in this section are probably better.

__ `Handling keywords with same names`_

Using other libraries directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because test libraries are technically just classes or modules, a
simple way to use another library is importing it and using its
methods. This approach works great when the methods are static and do
not depend on the library state. This is illustrated by the earlier
example that uses `Robot Framework's BuiltIn library`__.

If the library has state, however, things may not work as you would
hope.  The library instance you use in your library will not be the
same as the framework uses, and thus changes done by executed keywords
are not visible to your library. The next section explains how to get
an access to the same library instance that the framework uses.

__ `Using Robot Framework's internal modules`_

Getting active library instance from Robot Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BuiltIn_ keyword :name:`Get Library Instance` can be used to get the
currently active library instance from the framework itself. The
library instance returned by this keyword is the same as the framework
itself uses, and thus there is no problem seeing the correct library
state. Although this functionality is available as a keyword, it is
typically used in test libraries directly by importing the :name:`BuiltIn`
library class `as discussed earlier`__. The following example illustrates
how to implement the same :name:`Title Should Start With` keyword as in
the earlier example about `using inheritance`_.

__ `Using Robot Framework's internal modules`_

.. sourcecode:: python

   from robot.libraries.BuiltIn import BuiltIn

   def title_should_start_with(expected):
       seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
       title = seleniumlib.get_title()
       if not title.startswith(expected):
           raise AssertionError("Title '%s' did not start with '%s'"
                                % (title, expected))

This approach is clearly better than importing the library directly
and using it when the library has a state. The biggest benefit over
inheritance is that you can use the original library normally and use
the new library in addition to it when needed. That is demonstrated in
the example below where the code from the previous examples is
expected to be available in a new library :name:`SeLibExtensions`.

.. sourcecode:: robotframework

   *** Settings ***
   Library    SeleniumLibrary
   Library    SeLibExtensions

   *** Test Cases ***
   Example
       Open Browser    http://example      # SeleniumLibrary
       Title Should Start With    Example  # SeLibExtensions

Libraries using dynamic or hybrid API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test libraries that use the dynamic__ or `hybrid library API`_ often
have their own systems how to extend them. With these libraries you
need to ask guidance from the library developers or consult the
library documentation or source code.

__ `dynamic library API`_
