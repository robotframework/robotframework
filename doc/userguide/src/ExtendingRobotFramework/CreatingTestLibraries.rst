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
language. It is also possible to implement libraries with C
using `Python C API`__, although it is often easier to interact with
C code from Python libraries using ctypes__ module.

Libraries implemented using Python can
also act as wrappers to functionality implemented using other
programming languages. A good example of this approach is the `Remote
library`_, and another widely used approaches is running external
scripts or tools as separate processes.

__ http://docs.python.org/c-api/index.html
__ http://docs.python.org/library/ctypes.html

Different test library APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework has three different test library APIs.

Static API

  The simplest approach is having a module or a class
  with functions/methods which map directly to
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

__ `Keyword arguments`_
__ `Reporting keyword status`_
__ `Logging information`_
__ `Returning values`_

Creating test library class or module
-------------------------------------

Test libraries can be implemented as Python modules or classes.

Library name
~~~~~~~~~~~~

As discussed under the `Using test libraries`_ section, libraries can
be `imported by name or path`__:

.. sourcecode:: robotframework

   *** Settings ***
   Library    MyLibrary
   Library    module.LibraryClass
   Library    path/AnotherLibrary.py

When a library is imported by a name, the library module must be in the
`module search path`_ and the name can either refer to a library module
or to a library class. When a name refers directly to a library class,
the name must be in format like `modulename.ClassName`. Paths to libraries
always refer to modules.

Even when a library import refers to a module, either by a name or by a path,
a class in the module, not the module itself, is used as a library in these cases:

1. If the module contains a class that has the same name as the module.
   The class can be either implemented in the module or imported into it.

   This makes it possible to import libraries using simple names like `MyLibrary`
   instead of specifying both the module and the class like `module.MyLibrary` or
   `MyLibrary.MyLibrary`. When importing a library by a path, it is not even
   possible to directly refer to a library class and automatically using a class
   from the imported module is the only option.

2. If the module contains exactly one class decorated with the `@library decorator`_.
   In this case the class needs to be implemented in the module, not imported to it.

   This approach has all the same benefits as the earlier one, but it also allows
   the class name to differ from the module name.

   Using the `@library decorator`_ for this purpose is new in Robot Framework 7.2.

.. tip:: If the library name is really long, it is often a good idea to give
         it a `simpler alias`__ at the import time.

__ `Specifying library to import`_
__ `Setting custom name to library`_

Providing arguments to libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All test libraries implemented as classes can take arguments. These
arguments are specified after the library name when the library is imported,
and when Robot Framework creates an instance of the imported library,
it passes them to its constructor. Libraries implemented as a module
cannot take any arguments.

The number of arguments needed by the library is the same
as the number of arguments accepted by the library's `__init__` method.
The default values, argument conversion, and other such features work
the same way as with `keyword arguments`_. Arguments passed
to the library, as well as the library name itself, can be specified
using variables, so it is possible to alter them, for example, from the
command line.

.. sourcecode:: robotframework

   *** Settings ***
   Library    MyLibrary     10.0.0.1    8080
   Library    AnotherLib    ${ENVIRONMENT}

Example implementations for the libraries used in the above example:

.. sourcecode:: python

  from example import Connection

  class MyLibrary:

      def __init__(self, host, port=80):
          self.connection = Connection(host, port)

      def send_message(self, message):
          self.connection.send(message)

.. sourcecode:: python

   class AnotherLib:

       def __init__(self, environment):
           self.environment = environment

       def do_something(self):
           if self.environment == 'test':
               do_something_in_test_environment()
           else:
               do_something_in_other_environments()

Library scope
~~~~~~~~~~~~~

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

`TEST`
  A new instance is created for every test case. A possible suite setup
  and suite teardown share yet another instance.

  Prior to Robot Framework 3.2 this value was `TEST CASE`, but nowadays
  `TEST` is recommended. Because all unrecognized values are considered
  same as `TEST`, both values work with all versions. For the same reason
  it is possible to also use value `TASK` if the library is targeted for
  RPA_ usage more than testing. `TEST` is also the default value if the
  `ROBOT_LIBRARY_SCOPE` attribute is not set.


`SUITE`
  A new instance is created for every test suite. The lowest-level test
  suites, created from test case files and containing test cases, have
  instances of their own, and higher-level suites all get their own instances
  for their possible setups and teardowns.

  Prior to Robot Framework 3.2 this value was `TEST SUITE`. That value still
  works, but `SUITE` is recommended with libraries targeting Robot Framework
  3.2 and newer.

`GLOBAL`
  Only one instance is created during the whole test execution and it
  is shared by all test cases and test suites. Libraries created from
  modules are always global.

.. note:: If a library is imported multiple times with different arguments__,
          a new instance is created every time regardless the scope. If a 
          library is imported multiple times using the same destination
          the initial instance remains available unaffected by the new imports.

When the `SUITE` or `GLOBAL` scopes are used with libraries that have a state,
it is recommended that libraries have some
special keyword for cleaning up the state. This keyword can then be
used, for example, in a suite setup or teardown to ensure that test
cases in the next test suites can start from a known state. For example,
:name:`SeleniumLibrary` uses the `GLOBAL` scope to enable
using the same browser in different test cases without having to
reopen it, and it also has the :name:`Close All Browsers` keyword for
easily closing all opened browsers.

Example library using the `SUITE` scope:

.. sourcecode:: python

    class ExampleLibrary:
        ROBOT_LIBRARY_SCOPE = 'SUITE'

        def __init__(self):
            self._counter = 0

        def count(self):
            self._counter += 1
            print(self._counter)

        def clear_count(self):
            self._counter = 0

__ `Providing arguments to libraries`_

Library version
~~~~~~~~~~~~~~~

When a test library is taken into use, Robot Framework tries to
determine its version. This information is then written into the syslog_
to provide debugging information. Library documentation tool
Libdoc_ also writes this information into the keyword
documentations it generates.

Version information is read from attribute
`ROBOT_LIBRARY_VERSION`, similarly as `library scope`_ is
read from `ROBOT_LIBRARY_SCOPE`. If
`ROBOT_LIBRARY_VERSION` does not exist, information is tried to
be read from `__version__` attribute. These attributes must be
class or module attributes, depending whether the library is
implemented as a class or a module.

An example module using `__version__`:

.. sourcecode:: python

    __version__ = '0.1'

    def keyword():
        pass


Documentation format
~~~~~~~~~~~~~~~~~~~~

Library documentation tool Libdoc_
supports documentation in multiple formats. If you want to use something
else than Robot Framework's own `documentation formatting`_, you can specify
the format in the source code using  `ROBOT_LIBRARY_DOC_FORMAT` attribute
similarly as scope__ and version__ are set with their own
`ROBOT_LIBRARY_*` attributes.

The possible case-insensitive values for documentation format are
`ROBOT` (default), `HTML`, `TEXT` (plain text),
and `reST` (reStructuredText_). Using the `reST` format requires
the docutils_ module to be installed when documentation is generated.

Setting the documentation format is illustrated by the following example that
uses reStructuredText format.
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


__ `Library scope`_
__ `Library version`_

Library acting as listener
~~~~~~~~~~~~~~~~~~~~~~~~~~

`Listener interface`_ allows external listeners to get notifications about
test execution. They are called, for example, when suites, tests, and keywords
start and end. Sometimes getting such notifications is also useful for test
libraries, and they can register a custom listener by using
`ROBOT_LIBRARY_LISTENER` attribute. The value of this attribute
should be an instance of the listener to use, possibly the library itself.

For more information and examples see `Libraries as listeners`_ section.

`@library` decorator
~~~~~~~~~~~~~~~~~~~~

An easy way to configure libraries implemented as classes is using
the `robot.api.deco.library` class decorator. It allows configuring library's
scope__, version__, `custom argument converters`__, `documentation format`_
and listener__ with optional arguments `scope`, `version`, `converter`,
`doc_format` and `listener`, respectively. When these arguments are used, they
set the matching `ROBOT_LIBRARY_SCOPE`, `ROBOT_LIBRARY_VERSION`,
`ROBOT_LIBRARY_CONVERTERS`, `ROBOT_LIBRARY_DOC_FORMAT` and `ROBOT_LIBRARY_LISTENER`
attributes automatically:

.. sourcecode:: python

    from robot.api.deco import library

    from example import Listener


    @library(scope='GLOBAL', version='3.2b1', doc_format='reST', listener=Listener())
    class Example:
        ...

The `@library` decorator also disables the `automatic keyword discovery`__
by setting the `ROBOT_AUTO_KEYWORDS` argument to `False` by default. This
means that it is mandatory to decorate methods with the `@keyword decorator`_
to expose them as keywords. If only that behavior is desired and no further
configuration is needed, the decorator can also be used without parenthesis
like:

.. sourcecode:: python

    from robot.api.deco import library


    @library
    class Example:
        ...

If needed, the automatic keyword discovery can be enabled by using the
`auto_keywords` argument:

.. sourcecode:: python

    from robot.api.deco import library


    @library(scope='GLOBAL', auto_keywords=True)
    class Example:
        ...

The `@library` decorator only sets class attributes `ROBOT_LIBRARY_SCOPE`,
`ROBOT_LIBRARY_VERSION`, `ROBOT_LIBRARY_CONVERTERS`, `ROBOT_LIBRARY_DOC_FORMAT`
and `ROBOT_LIBRARY_LISTENER` if the respective arguments `scope`, `version`,
`converters`, `doc_format` and `listener` are used. The `ROBOT_AUTO_KEYWORDS`
attribute is set always and its presence can be used as an indication that
the `@library` decorator has been used. When attributes are set, they
override possible existing class attributes.

When a class is decorated with the `@library` decorator, it is used as a library
even when a `library import refers only to a module containing it`__. This is done
regardless does the the class name match the module name or not.

.. note:: The `@library` decorator is new in Robot Framework 3.2,
          the `converters` argument is new in Robot Framework 5.0, and
          specifying that a class in an imported module should be used as
          a library is new in Robot Framework 7.2.

__ `library scope`_
__ `library version`_
__ `Custom argument converters`_
__ `Library acting as listener`_
__ `What methods are considered keywords`_
__ `Library name`_

Creating keywords
-----------------

What methods are considered keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the static library API is used, Robot Framework uses introspection
to find out what keywords the library class or module implements.
By default it excludes methods and functions starting with an underscore.
All the methods and functions that are not ignored are considered keywords.
For example, the library below implements a single keyword :name:`My Keyword`.

.. sourcecode:: python

    class MyLibrary:

        def my_keyword(self, arg):
            return self._helper_method(arg)

        def _helper_method(self, arg):
            return arg.upper()


Limiting public methods becoming keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Automatically considering all public methods and functions keywords typically
works well, but there are cases where it is not desired. There are also
situations where keywords are created when not expected. For example, when
implementing a library as class, it can be a surprise that also methods
in possible base classes are considered keywords. When implementing a library
as a module, functions imported into the module namespace becoming keywords
is probably even a bigger surprise.

This section explains how to prevent methods and functions becoming keywords.

Class based libraries
'''''''''''''''''''''

When a library is implemented as a class, it is possible to tell
Robot Framework not to automatically expose methods as keywords by setting
the `ROBOT_AUTO_KEYWORDS` attribute to the class with a false value:

.. sourcecode:: python

   class Example:
       ROBOT_AUTO_KEYWORDS = False

When the `ROBOT_AUTO_KEYWORDS` attribute is set like this, only methods that
have explicitly been decorated with the `@keyword decorator`_ or otherwise
have the `robot_name` attribute become keywords. The `@keyword` decorator
can also be used for setting a `custom name`__, tags__ and `argument types`__
to the keyword.

Although the `ROBOT_AUTO_KEYWORDS` attribute can be set to the class
explicitly, it is more convenient to use the `@library decorator`_
that sets it to `False` by default:

.. sourcecode:: python

   from robot.api.deco import keyword, library


   @library
   class Example:

       @keyword
       def this_is_keyword(self):
           pass

       @keyword('This is keyword with custom name')
       def xxx(self):
           pass

       def this_is_not_keyword(self):
           pass

.. note:: Both limiting what methods become keywords using the
          `ROBOT_AUTO_KEYWORDS` attribute and the `@library` decorator are
          new in Robot Framework 3.2.

Another way to explicitly specify what keywords a library implements is using
the dynamic__ or the hybrid__ library API.

__ `Setting custom name`_
__ `Keyword tags`_
__ `Specifying argument types using @keyword decorator`_
__ `Dynamic library API`_
__ `Hybrid library API`_

Module based libraries
''''''''''''''''''''''

When implementing a library as a module, all functions in the module namespace
become keywords. This is true also with imported functions, and that can cause
nasty surprises. For example, if the module below would be used as a library,
it would contain a keyword :name:`Example Keyword`, as expected, but also
a keyword :name:`Current Thread`.

.. sourcecode:: python

   from threading import current_thread


   def example_keyword():
       thread_name = current_thread().name
       print(f"Running in thread '{thread_name}'.")

A simple way to avoid imported functions becoming keywords is to only
import modules (e.g. `import threading`) and to use functions via the module
(e.g `threading.current_thread()`). Alternatively functions could be
given an alias starting with an underscore at the import time (e.g.
`from threading import current_thread as _current_thread`).

A more explicit way to limit what functions become keywords is using
the module level `__all__` attribute that `Python itself uses for similar
purposes`__. If it is used, only the listed functions can be keywords.
For example, the library below implements only one keyword
:name:`Example Keyword`:

.. sourcecode:: python

   from threading import current_thread


   __all__ = ['example_keyword']


   def example_keyword():
       thread_name = current_thread().name
       print(f"Running in thread '{thread_name}'.")

   def this_is_not_keyword():
       pass

If the library is big, maintaining the `__all__` attribute when keywords are
added, removed or renamed can be a somewhat big task. Another way to explicitly
mark what functions are keywords is using the `ROBOT_AUTO_KEYWORDS` attribute
similarly as it can be used with `class based libraries`_. When this attribute
is set to a false value, only functions explicitly decorated with the
`@keyword decorator`_ become keywords. For example, also this library
implements only one keyword :name:`Example Keyword`:

.. sourcecode:: python

   from threading import current_thread

   from robot.api.deco import keyword


   ROBOT_AUTO_KEYWORDS = False


   @keyword
   def example_keyword():
       thread_name = current_thread().name
       print(f"Running in thread '{thread_name}'.")

   def this_is_not_keyword():
       pass

.. note:: Limiting what functions become keywords using `ROBOT_AUTO_KEYWORDS`
          is a new feature in Robot Framework 3.2.

__ https://docs.python.org/tutorial/modules.html#importing-from-a-package

Using `@not_keyword` decorator
''''''''''''''''''''''''''''''

Functions in modules and methods in classes can be explicitly marked as
"not keywords" by using the `@not_keyword` decorator. When a library is
implemented as a module, this decorator can also be used to avoid imported
functions becoming keywords.

.. sourcecode:: python

   from threading import current_thread

   from robot.api.deco import not_keyword


   not_keyword(current_thread)    # Don't expose `current_thread` as a keyword.


   def example_keyword():
       thread_name = current_thread().name
       print(f"Running in thread '{thread_name}'.")

   @not_keyword
   def this_is_not_keyword():
       pass

Using the `@not_keyword` decorator is pretty much the opposite way to avoid
functions or methods becoming keywords compared to disabling the automatic
keyword discovery with the `@library` decorator or by setting the
`ROBOT_AUTO_KEYWORDS` to a false value. Which one to use depends on the context.

.. note:: The `@not_keyword` decorator is new in Robot Framework 3.2.

Keyword names
~~~~~~~~~~~~~

Keyword names used in the test data are compared with method names to
find the method implementing these keywords. Name comparison is
case-insensitive, and also spaces and underscores are ignored. For
example, the method `hello` maps to the keyword name
:name:`Hello`, :name:`hello` or even :name:`h e l l o`. Similarly both the
`do_nothing` and `doNothing` methods can be used as the
:name:`Do Nothing` keyword in the test data.

Example library implemented as a module in the :file:`MyLibrary.py` file:

.. sourcecode:: python

  def hello(name):
      print(f"Hello, {name}!")

  def do_nothing():
      pass


The example below illustrates how the example library above can be
used. If you want to try this yourself, make sure that the library is
in the `module search path`_.

.. sourcecode:: robotframework

   *** Settings ***
   Library    MyLibrary

   *** Test Cases ***
   My Test
       Do Nothing
       Hello    world

Setting custom name
'''''''''''''''''''

It is possible to expose a different name for a keyword instead of the
default keyword name which maps to the method name.  This can be accomplished
by setting the `robot_name` attribute on the method to the desired custom name:

.. sourcecode:: python

    def login(username, password):
        ...

    login.robot_name = 'Login via user panel'

.. sourcecode:: robotframework

    *** Test Cases ***
    My Test
        Login Via User Panel    ${username}    ${password}

Instead of explicitly setting the `robot_name` attribute like in the above
example, it is typically easiest to use the `@keyword decorator`_:

.. sourcecode:: python

    from robot.api.deco import keyword


    @keyword('Login via user panel')
    def login(username, password):
        ...

Using this decorator without an argument will have no effect on the exposed
keyword name, but will still set the `robot_name` attribute.  This allows
`marking methods to expose as keywords`_ without actually changing keyword
names. Methods that have the `robot_name`
attribute also create keywords even if the method name itself would start with
an underscore.

Setting a custom keyword name can also enable library keywords to accept
arguments using the `embedded arguments`__ syntax.

__ `Embedding arguments into keyword names`_

Keyword tags
~~~~~~~~~~~~

Library keywords and `user keywords`__ can have tags. Library keywords can
define them by setting the `robot_tags` attribute on the method to a list
of desired tags. Similarly as when `setting custom name`_, it is easiest to
set this attribute by using the `@keyword decorator`_:

.. sourcecode:: python

    from robot.api.deco import keyword


    @keyword(tags=['tag1', 'tag2'])
    def login(username, password):
        ...

    @keyword('Custom name', ['tags', 'here'])
    def another_example():
        ...

Another option for setting tags is giving them on the last line of
`keyword documentation`__ with `Tags:` prefix and separated by a comma. For
example:

.. sourcecode:: python

    def login(username, password):
        """Log user in to SUT.

        Tags: tag1, tag2
        """
        ...

__ `User keyword tags`_
__ `Documenting libraries`_

Keyword arguments
~~~~~~~~~~~~~~~~~

With a static and hybrid API, the information on how many arguments a
keyword needs is got directly from the method that implements it.
Libraries using the `dynamic library API`_ have other means for sharing
this information, so this section is not relevant to them.

The most common and also the simplest situation is when a keyword needs an
exact number of arguments. In this case, the method
simply take exactly those arguments. For example, a method implementing a
keyword with no arguments takes no arguments either, a method
implementing a keyword with one argument also takes one argument, and
so on.

Example keywords taking different numbers of arguments:

.. sourcecode:: python

  def no_arguments():
      print("Keyword got no arguments.")

  def one_argument(arg):
      print(f"Keyword got one argument '{arg}'.")

  def three_arguments(a1, a2, a3):
      print(f"Keyword got three arguments '{a1}', '{a2}' and '{a3}'.")


Default values to keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~

It is often useful that some of the arguments that a keyword uses have
default values.

In Python a method has always exactly one implementation and possible
default values are specified in the method signature. The syntax,
which is familiar to all Python programmers, is illustrated below:

.. sourcecode:: python

   def one_default(arg='default'):
       print(f"Got argument '{arg}'.")


   def multiple_defaults(arg1, arg2='default 1', arg3='default 2'):
       print(f"Got arguments '{arg1}', '{arg2}' and '{arg3}'.")

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


.. _varargs-library:

Variable number of arguments (`*varargs`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework supports also keywords that take any number of
arguments.

Python supports methods accepting any number of arguments. The same
syntax works in libraries and, as the examples below show, it can also
be combined with other ways of specifying arguments:

.. sourcecode:: python

  def any_arguments(*args):
      print("Got arguments:")
      for arg in args:
          print(arg)

  def one_required(required, *others):
      print(f"Required: {required}\nOthers:")
      for arg in others:
          print(arg)

  def also_defaults(req, def1="default 1", def2="default 2", *rest):
      print(req, def1, def2, rest)

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


.. _kwargs-library:

Free keyword arguments (`**kwargs`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework supports `Python's **kwargs syntax`__.
How to use use keywords that accept *free keyword arguments*,
also known as *free named arguments*, is `discussed under the Creating test
cases section`__. In this section we take a look at how to create such keywords.

If you are already familiar how kwargs work with Python, understanding how
they work with Robot Framework test libraries is rather simple. The example
below shows the basic functionality:

.. sourcecode:: python

    def example_keyword(**stuff):
        for name, value in stuff.items():
            print(name, value)

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

  def various_args(arg=None, *varargs, **kwargs):
      if arg is not None:
          print('arg:', arg)
      for value in varargs:
          print('vararg:', value)
      for name, value in sorted(kwargs.items()):
          print('kwarg:', name, value)

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

__ https://docs.python.org/tutorial/controlflow.html#keyword-arguments
__ `Free named arguments`_
__ Escaping_

Keyword-only arguments
~~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 3.1, it is possible to use `named-only arguments`_
with different keywords. This support
is provided by Python's `keyword-only arguments`__. Keyword-only arguments
are specified after possible `*varargs` or after a dedicated `*` marker when
`*varargs` are not needed. Possible `**kwargs` are specified after keyword-only
arguments.

Example:

.. sourcecode:: python

    def sort_words(*words, case_sensitive=False):
        key = str.lower if case_sensitive else None
        return sorted(words, key=key)

    def strip_spaces(word, *, left=True, right=True):
        if left:
            word = word.lstrip()
        if right:
            word = word.rstrip()
        return word

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       Sort Words    Foo    bar    baZ
       Sort Words    Foo    bar    baZ    case_sensitive=True
       Strip Spaces    ${word}    left=False

__ https://www.python.org/dev/peps/pep-3102

Positional-only arguments
~~~~~~~~~~~~~~~~~~~~~~~~~

Python supports so called `positional-only arguments`__ that make it possible to
specify that an argument can only be given as a `positional argument`_, not as
a `named argument`_ like `name=value`. Positional-only arguments are specified
before normal arguments and a special `/` marker must be used after them:

.. sourcecode:: python

    def keyword(posonly, /, normal):
        print(f"Got positional-only argument {posonly} and normal argument {normal}.")

The above keyword could be used like this:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       # Positional-only and normal argument used as positional arguments.
       Keyword    foo    bar
       # Normal argument can also be named.
       Keyword    foo    normal=bar

If a positional-only argument is used with a value that contains an equal sign
like `example=usage`, it is not considered to mean `named argument syntax`_
even if the part before the `=` would match the argument name. This rule
only applies if the positional-only argument is used in its correct position
without other arguments using the name argument syntax before it, though.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       # Positional-only argument gets literal value `posonly=foo` in this case.
       Keyword    posonly=foo    normal=bar
       # This fails.
       Keyword    normal=bar    posonly=foo

Positional-only arguments are fully supported starting from Robot Framework 4.0.
Using them as positional arguments works also with earlier versions,
but using them as named arguments causes an error on Python side.

__ https://www.python.org/dev/peps/pep-0570/

Argument conversion
~~~~~~~~~~~~~~~~~~~

Arguments defined in Robot Framework test data are, by default,
passed to keywords as Unicode strings. There are, however, several ways
to use non-string values as well:

- Variables_ can contain any kind of objects as values, and variables used
  as arguments are passed to keywords as-is.
- Keywords can themselves `convert arguments they accept`__ to other types.
- It is possible to specify argument types explicitly using
  `function annotations`__ or the `@keyword decorator`__. In these cases
  Robot Framework converts arguments automatically.
- Automatic conversion is also done based on `keyword default values`__.
- Libraries can register `custom argument converters`_.

Automatic argument conversion based on function annotations, types specified
using the `@keyword` decorator, and argument default values are all new
features in Robot Framework 3.1. The `Supported conversions`_ section
specifies which argument conversion are supported in these cases.

Prior to Robot Framework 4.0, automatic conversion was done only if the given
argument was a string. Nowadays it is done regardless the argument type.

__ `Manual argument conversion`_
__ `Specifying argument types using function annotations`_
__ `Specifying argument types using @keyword decorator`_
__ `Implicit argument types based on default values`_

Manual argument conversion
''''''''''''''''''''''''''

If no type information is specified to Robot Framework, all arguments not
passed as variables_ are given to keywords as Unicode strings. This includes
cases like this:

.. sourcecode:: robotframework

  *** Test Cases ***
  Example
      Example Keyword    42    False

It is always possible to convert arguments passed as strings insider keywords.
In simple cases this means using `int()` or `float()` to convert arguments
to numbers, but other kind of conversion is possible as well. When working
with Boolean values, care must be taken because all non-empty strings,
including string `False`, are considered true by Python. Robot Framework's own
`robot.utils.is_truthy()` utility handles this nicely as it considers strings
like `FALSE`, `NO` and `NONE` (case-insensitively) to be false:

.. sourcecode:: python

  from robot.utils import is_truthy


  def example_keyword(count, case_insensitive):
      count = int(count)
      if is_truthy(case_insensitive):
          ...

Keywords can also use Robot Framework's argument conversion functionality via
the `robot.api.TypeInfo`__ class and its `convert` method. This can be useful
if the needed conversion logic is more complicated or the are needs for better
error reporting than what simply using, for example, `int()` provides.

.. sourcecode:: python

  from robot.api import TypeInfo


  def example_keyword(count, case_insensitive):
      count = TypeInfo.from_type(int).convert(count)
      if TypeInfo.from_type(bool).convert(case_insensitive):
          ...

.. tip:: It is generally recommended to specify types using type hints or otherwise
         and let Robot Framework handle argument conversion automatically. Manual
         argument conversion should only be needed in special cases.

.. note:: `robot.api.TypeInfo` is new in Robot Framework 7.0.

__ https://robot-framework.readthedocs.io/en/stable/autodoc/robot.running.arguments.html#robot.running.arguments.typeinfo.TypeInfo

Specifying argument types using function annotations
''''''''''''''''''''''''''''''''''''''''''''''''''''

Starting from Robot Framework 3.1, arguments passed to keywords are automatically
converted if argument type information is available and the type is recognized.
The most natural way to specify types is using Python `function annotations`_.
For example, the keyword in the previous example could be implemented as
follows and arguments would be converted automatically:

.. sourcecode:: python

  def example_keyword(count: int, case_insensitive: bool = True):
      if case_insensitive:
          ...

See the `Supported conversions`_ section below for a list of types that
are automatically converted and what values these types accept. It is
an error if an argument having one of the supported types is given
a value that cannot be converted. Annotating only some of the arguments
is fine.

Annotating arguments with other than the supported types is not an error,
and it is also possible to use annotations for other than typing
purposes. In those cases no conversion is done, but annotations are
nevertheless shown in the documentation generated by Libdoc_.

Keywords can also have a return type annotation specified using the `->`
notation at the end of the signature like `def example() -> int:`.
This information is not used for anything during execution, but starting from
Robot Framework 7.0 it is shown by Libdoc_ for documentation purposes.

.. _function annotations: https://www.python.org/dev/peps/pep-3107/

Specifying argument types using `@keyword` decorator
''''''''''''''''''''''''''''''''''''''''''''''''''''

An alternative way to specify explicit argument types is using the
`@keyword decorator`_. Starting from Robot Framework 3.1,
it accepts an optional `types` argument that can be used to specify argument
types either as a dictionary mapping argument names to types or as a list
mapping arguments to types based on position. These approaches are shown
below implementing the same keyword as in earlier examples:

.. sourcecode:: python

  from robot.api.deco import keyword


  @keyword(types={'count': int, 'case_insensitive': bool})
  def example_keyword(count, case_insensitive=True):
      if case_insensitive:
          ...

  @keyword(types=[int, bool])
  def example_keyword(count, case_insensitive=True):
      if case_insensitive:
          ...

Regardless of the approach that is used, it is not necessarily to specify
types for all arguments. When specifying types as a list, it is possible
to use `None` to mark that a certain argument does not have type information
and arguments at the end can be omitted altogether. For example, both of these
keywords specify the type only for the second argument:

.. sourcecode:: python

  @keyword(types={'second': float})
  def example1(first, second, third):
      ...

  @keyword(types=[None, float])
  def example2(first, second, third):
      ...

Starting from Robot Framework 7.0, it is possible to specify the keyword return
type by using key `'return'` with an appropriate type in the type dictionary.
This information is not used for anything during execution, but it is shown by
Libdoc_ for documentation purposes.

If any types are specified using the `@keyword` decorator, type information
got from annotations__ is ignored with that keyword. Setting `types` to `None`
like `@keyword(types=None)` disables type conversion altogether so that also
type information got from `default values`__ is ignored.

__ `Specifying argument types using function annotations`_
__ `Implicit argument types based on default values`_

Implicit argument types based on default values
'''''''''''''''''''''''''''''''''''''''''''''''

If type information is not got explicitly using annotations or the `@keyword`
decorator, Robot Framework 3.1 and newer tries to get it based on possible
argument default value. In this example `count` and `case_insensitive` get
types `int` and `bool`, respectively:

.. sourcecode:: python

  def example_keyword(count=-1, case_insensitive=True):
      if case_insensitive:
          ...

When type information is got implicitly based on the default values,
argument conversion itself is not as strict as when the information is
got explicitly:

- Conversion may be attempted also to other "similar" types. For example,
  if converting to an integer fails, float conversion is attempted.

- Conversion failures are not errors, keywords get the original value in
  these cases instead.

If an argument has an explicit type and a default value, conversion is first
attempted based on the explicit type. If that fails, then conversion is attempted
based on the default value. In this special case conversion based on the default
value is strict and a conversion failure causes an error.

If argument conversion based on default values is not desired, the whole
argument conversion can be disabled with the `@keyword decorator`__ like
`@keyword(types=None)`.

.. note:: Prior to Robot Framework 4.0 conversion was done based on the default
          value only if the argument did not have an explict type.

__ `Specifying argument types using @keyword decorator`_

Supported conversions
'''''''''''''''''''''

The table below lists the types that Robot Framework 3.1 and newer convert
arguments to. These characteristics apply to all conversions:

- Type can be explicitly specified using `function annotations`__ or
  the `@keyword decorator`__.
- If not explicitly specified, type can be got implicitly from `argument
  default values`__.
- Conversion is done regardless of the type of the given argument. If the
  argument type is incompatible with the expected type, conversion fails.
- Conversion failures cause an error if the type has been specified explicitly.
  If the type is got based on a default value, the given argument is used as-is.

__ `Specifying argument types using function annotations`_
__ `Specifying argument types using @keyword decorator`_
__ `Implicit argument types based on default values`_

.. note:: If an argument has both a type hint and a default value, conversion is
          first attempted based on the type hint and then, if that fails, based on
          the default value type. This behavior is likely to change in the future
          so that conversion based on the default value is done *only* if the argument
          does not have a type hint. That will change conversion behavior in cases
          like `arg: list = None` where `None` conversion will not be attempted
          anymore. Library creators are strongly recommended to specify the default
          value type explicitly like `arg: list | None = None` already now.

The type to use can be specified either using concrete types (e.g. list_),
by using abstract base classes (ABC) (e.g. Sequence_), or by using sub
classes of these types (e.g. MutableSequence_). Also types in in the typing_
module that map to the supported concrete types or ABCs (e.g. `List`) are
supported. In all these cases the argument is converted to the concrete type.

In addition to using the actual types (e.g. `int`), it is possible to specify
the type using type names as a string (e.g. `'int'`) and some types also have
aliases (e.g. `'integer'`). Matching types to names and aliases is
case-insensitive.

The Accepts column specifies which given argument types are converted.
If the given argument already has the expected type, no conversion is done.
Other types cause conversion failures.

.. table:: Supported argument conversions
   :class: tabular
   :widths: 5 5 5 5 60 20

   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   |     Type     |      ABC      |  Aliases   |   Accepts    |                       Explanation                              |             Examples                 |
   +==============+===============+============+==============+================================================================+======================================+
   | bool_        |               | boolean    | str_,        | Strings `TRUE`, `YES`, `ON` and `1` are converted to `True`,   | | `TRUE` (converted to `True`)       |
   |              |               |            | int_,        | the empty string as well as `FALSE`, `NO`, `OFF` and `0`       | | `off` (converted to `False`)       |
   |              |               |            | float_,      | are converted to `False`, and the string `NONE` is converted   | | `example` (used as-is)             |
   |              |               |            | None_        | to `None`. Other strings and other accepted values are         |                                      |
   |              |               |            |              | passed as-is, allowing keywords to handle them specially if    |                                      |
   |              |               |            |              | needed. All string comparisons are case-insensitive.           |                                      |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | True and false strings can be localized_. See the              |                                      |
   |              |               |            |              | Translations_ appendix for supported translations.             |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | int_         | Integral_     | integer,   | str_,        | Conversion is done using the int_ built-in function. Floats    | | `42`                               |
   |              |               | long       | float_       | are accepted only if they can be represented as integers       | | `-1`                               |
   |              |               |            |              | exactly. For example, `1.0` is accepted and `1.1` is not.      | | `10 000 000`                       |
   |              |               |            |              | If converting a string to an integer fails and the type        | | `1e100`                            |
   |              |               |            |              | is got implicitly based on a default value, conversion to      | | `0xFF`                             |
   |              |               |            |              | float is attempted as well.                                    | | `0o777`                            |
   |              |               |            |              |                                                                | | `0b1010`                           |
   |              |               |            |              | Starting from Robot Framework 4.1, it is possible to use       | | `0xBAD_C0FFEE`                     |
   |              |               |            |              | hexadecimal, octal and binary numbers by prefixing values with | | `${1}`                             |
   |              |               |            |              | `0x`, `0o` and `0b`, respectively.                             | | `${1.0}`                           |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | Starting from Robot Framework 4.1, spaces and underscores can  |                                      |
   |              |               |            |              | be used as visual separators for digit grouping purposes.      |                                      |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | Starting from Robot Framework 7.0, strings representing floats |                                      |
   |              |               |            |              | are accepted as long as their decimal part is zero. This       |                                      |
   |              |               |            |              | includes using the scientific notation like `1e100`.           |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | float_       | Real_         | double     | str_,        | Conversion is done using the float_ built-in.                  | | `3.14`                             |
   |              |               |            | Real_        |                                                                | | `2.9979e8`                         |
   |              |               |            |              | Starting from Robot Framework 4.1, spaces and underscores can  | | `10 000.000 01`                    |
   |              |               |            |              | be used as visual separators for digit grouping purposes.      | | `10_000.000_01`                    |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | Decimal_     |               |            | str_,        | Conversion is done using the Decimal_ class. Decimal_ is       | | `3.14`                             |
   |              |               |            | int_,        | recommended over float_ when decimal numbers need to be        | | `10 000.000 01`                    |
   |              |               |            | float_       | represented exactly.                                           | | `10_000.000_01`                    |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | Starting from Robot Framework 4.1, spaces and underscores can  |                                      |
   |              |               |            |              | be used as visual separators for digit grouping purposes.      |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | str_         |               | string,    | Any          | All arguments are converted to Unicode strings.                |                                      |
   |              |               | unicode    |              |                                                                |                                      |
   |              |               |            |              | New in Robot Framework 4.0.                                    |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | bytes_       |               |            | str_,        | Strings are converted to bytes so that each Unicode code point | | `good`                             |
   |              |               |            | bytearray_   | below 256 is directly mapped to a matching byte. Higher code   | | `hyvä` (converted to `hyv\xe4`)    |
   |              |               |            |              | points are not allowed.                                        | | `\x00` (the null byte)             |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | bytearray_   |               |            | str_,        | Same conversion as with bytes_, but the result is a bytearray_.|                                      |
   |              |               |            | bytes_       |                                                                |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | `datetime    |               |            | str_,        | Strings are expected to be timestamps in `ISO 8601`_ like      | | `2022-02-09T16:39:43.632269`       |
   | <dt-mod_>`__ |               |            | int_,        | format `YYYY-MM-DD hh:mm:ss.mmmmmm`, where any non-digit       | | `2022-02-09 16:39`                 |
   |              |               |            | float_       | character can be used as a separator or separators can be      | | `2022-02-09`                       |
   |              |               |            |              | omitted altogether. Additionally, only the date part is        | | `${1644417583.632269}` (Epoch time)|
   |              |               |            |              | mandatory, all possibly missing time components are considered |                                      |
   |              |               |            |              | to be zeros.                                                   |                                      |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | Integers and floats are considered to represent seconds since  |                                      |
   |              |               |            |              | the `Unix epoch`_.                                             |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | date_        |               |            | str_         | Same string conversion as with `datetime <dt-mod_>`__, but all | | `2018-09-12`                       |
   |              |               |            |              | time components are expected to be omitted or to be zeros.     |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | timedelta_   |               |            | str_,        | Strings are expected to represent a time interval in one of    | | `42` (42 seconds)                  |
   |              |               |            | int_,        | the time formats Robot Framework supports: `time as number`_,  | | `1 minute 2 seconds`               |
   |              |               |            | float_       | `time as time string`_ or `time as "timer" string`_. Integers  | | `01:02` (same as above)            |
   |              |               |            |              | and floats are considered to be seconds.                       |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | `Path        | PathLike_     |            | str_         | Strings are converted to `pathlib.Path <pathlib_>`__ objects.  | | `/tmp/absolute/path`               |
   | <pathlib_>`__|               |            |              | On Windows `/` is converted to :codesc:`\\` automatically.     | | `relative/path/to/file.ext`        |
   |              |               |            |              |                                                                | | `name.txt`                         |
   |              |               |            |              | New in Robot Framework 6.0.                                    |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | Enum_        |               |            | str_         | The specified type must be an enumeration (a subclass of Enum_ | .. sourcecode:: python               |
   |              |               |            |              | or Flag_) and given arguments must match its member names.     |                                      |
   |              |               |            |              |                                                                |    class Direction(Enum):            |
   |              |               |            |              | Matching member names is case, space, underscore and hyphen    |        """Move direction."""         |
   |              |               |            |              | insensitive, but exact matches have precedence over normalized |        NORTH = auto()                |
   |              |               |            |              | matches. Ignoring hyphens is new in Robot Framework 7.0.       |        NORTH_WEST = auto()           |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | Enumeration documentation and members are shown in             |    def kw(arg: Direction):           |
   |              |               |            |              | documentation generated by Libdoc_ automatically.              |        ...                           |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              |                                                                | | `NORTH` (Direction.NORTH)          |
   |              |               |            |              |                                                                | | `north west` (Direction.NORTH_WEST)|
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | IntEnum_     |               |            | str_,        | The specified type must be an integer based enumeration (a     | .. sourcecode:: python               |
   |              |               |            | int_         | subclass of IntEnum_ or IntFlag_) and given arguments must     |                                      |
   |              |               |            |              | match its member names or values.                              |    class PowerState(IntEnum):        |
   |              |               |            |              |                                                                |        """Turn system ON or OFF."""  |
   |              |               |            |              | Matching member names works the same way as with `Enum`.       |        OFF = 0                       |
   |              |               |            |              | Values can be given as integers and as strings that can be     |        ON = 1                        |
   |              |               |            |              | converted to integers.                                         |                                      |
   |              |               |            |              |                                                                |    def kw(arg: PowerState):          |
   |              |               |            |              | Enumeration documentation and members are shown in             |        ...                           |
   |              |               |            |              | documentation generated by Libdoc_ automatically.              |                                      |
   |              |               |            |              |                                                                | | `OFF` (PowerState.OFF)             |
   |              |               |            |              | New in Robot Framework 4.1.                                    | | `1` (PowerState.ON)                |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | Literal_     |               |            | Any          | Only specified values are accepted. Values can be strings,     | .. sourcecode:: python               |
   |              |               |            |              | integers, bytes, Booleans, enums and `None`, and used arguments|                                      |
   |              |               |            |              | are converted using the value type specific conversion logic.  |    def kw(arg: Literal['ON', 'OFF']):|
   |              |               |            |              |                                                                |        ...                           |
   |              |               |            |              | Strings are case, space, underscore and hyphen insensitive,    |                                      |
   |              |               |            |              | but exact matches have precedence over normalized matches.     | | `OFF`                              |
   |              |               |            |              |                                                                | | `on`                               |
   |              |               |            |              | `Literal` provides similar functionality as `Enum`, but does   |                                      |
   |              |               |            |              | not support custom documentation.                              |                                      |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | New in Robot Framework 7.0.                                    |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | None_        |               |            | str_         | String `NONE` (case-insensitive) is converted to the Python    | | `None`                             |
   |              |               |            |              | `None` object. Other values cause an error.                    |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | Any_         |               |            | Any          | Any value is accepted. No conversion is done.                  |                                      |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | New in Robot Framework 6.1.                                    |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | list_        | Sequence_     | sequence   | str_,        | Strings must be Python list literals. They are converted       | | `['one', 'two']`                   |
   |              |               |            | Sequence_    | to actual lists using the `ast.literal_eval`_ function.        | | `[('one', 1), ('two', 2)]`         |
   |              |               |            |              | They can contain any values `ast.literal_eval` supports,       |                                      |
   |              |               |            |              | including lists and other containers.                          |                                      |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | If the used type hint is list_ (e.g. `arg: list`), sequences   |                                      |
   |              |               |            |              | that are not lists are converted to lists. If the type hint is |                                      |
   |              |               |            |              | generic Sequence_, sequences are used without conversion.      |                                      |
   |              |               |            |              |                                                                |                                      |
   |              |               |            |              | Alias `sequence` is new in Robot Framework 7.0.                |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | tuple_       |               |            | str_,        | Same as `list`, but string arguments must tuple literals.      | | `('one', 'two')`                   |
   |              |               |            | Sequence_    |                                                                |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | set_         | `Set          |            | str_,        | Same as `list`, but string arguments must be set literals or   | | `{1, 2, 3, 42}`                    |
   |              | <abc.Set_>`__ |            | Container_   | `set()` to create an empty set.                                | | `set()`                            |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | frozenset_   |               |            | str_,        | Same as `set`, but the result is a frozenset_.                 | | `{1, 2, 3, 42}`                    |
   |              |               |            | Container_   |                                                                | | `frozenset()`                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | dict_        | Mapping_      | dictionary,| str_,        | Same as `list`, but string arguments must be dictionary        | | `{'a': 1, 'b': 2}`                 |
   |              |               | mapping,   | Mapping_     | literals.                                                      | | `{'key': 1, 'nested': {'key': 2}}` |
   |              |               | map        |              |                                                                |                                      |
   |              |               |            |              | Alias `mapping` is new in Robot Framework 7.0.                 |                                      |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+
   | TypedDict_   |               |            | str_,        | Same as `dict`, but dictionary items are also converted        | .. sourcecode:: python               |
   |              |               |            | Mapping_     | to the specified types and items not included in the type      |                                      |
   |              |               |            |              | spec are not allowed.                                          |    class Config(TypedDict):          |
   |              |               |            |              |                                                                |        width: int                    |
   |              |               |            |              | New in Robot Framework 6.0. Normal `dict` conversion was       |        enabled: bool                 |
   |              |               |            |              | used earlier.                                                  |                                      |
   |              |               |            |              |                                                                | | `{'width': 1600, 'enabled': True}` |
   +--------------+---------------+------------+--------------+----------------------------------------------------------------+--------------------------------------+

.. note:: Starting from Robot Framework 5.0, types that have a converted are
          automatically shown in Libdoc_ outputs.

.. note:: Prior to Robot Framework 4.0, most types supported converting string `NONE` (case-insensitively) to Python
          `None`. That support has been removed and `None` conversion is only done if an argument has `None` as an
          explicit type or as a default value.

.. _Any: https://docs.python.org/library/typing.html#typing.Any
.. _bool: https://docs.python.org/library/functions.html#bool
.. _int: https://docs.python.org/library/functions.html#int
.. _Integral: https://docs.python.org/library/numbers.html#numbers.Integral
.. _float: https://docs.python.org/library/functions.html#float
.. _Real: https://docs.python.org/library/numbers.html#numbers.Real
.. _Decimal: https://docs.python.org/library/decimal.html#decimal.Decimal
.. _str: https://docs.python.org/library/functions.html#func-str
.. _bytes: https://docs.python.org/library/functions.html#func-bytes
.. _bytearray: https://docs.python.org/library/functions.html#func-bytearray
.. _dt-mod: https://docs.python.org/library/datetime.html#datetime.datetime
.. _date: https://docs.python.org/library/datetime.html#datetime.date
.. _timedelta: https://docs.python.org/library/datetime.html#datetime.timedelta
.. _pathlib: https://docs.python.org/library/pathlib.html
.. _PathLike: https://docs.python.org/library/os.html#os.PathLike
.. _Enum: https://docs.python.org/library/enum.html#enum.Enum
.. _Flag: https://docs.python.org/library/enum.html#enum.Flag
.. _IntEnum: https://docs.python.org/library/enum.html#enum.IntEnum
.. _IntFlag: https://docs.python.org/library/enum.html#enum.IntFlag
.. _Literal: https://docs.python.org/library/typing.html#typing.Literal
.. _None: https://docs.python.org/library/constants.html#None
.. _list: https://docs.python.org/library/stdtypes.html#list
.. _Sequence: https://docs.python.org/library/collections.abc.html#collections.abc.Sequence
.. _MutableSequence: https://docs.python.org/library/collections.abc.html#collections.abc.MutableSequence
.. _tuple: https://docs.python.org/library/stdtypes.html#tuple
.. _dict: https://docs.python.org/library/stdtypes.html#dict
.. _Mapping: https://docs.python.org/library/collections.abc.html#collections.abc.Mapping
.. _set: https://docs.python.org/library/stdtypes.html#set
.. _abc.Set: https://docs.python.org/library/collections.abc.html#collections.abc.Set
.. _frozenset: https://docs.python.org/library/stdtypes.html#frozenset
.. _TypedDict: https://docs.python.org/library/typing.html#typing.TypedDict
.. _Container: https://docs.python.org/library/collections.abc.html#collections.abc.Container
.. _typing: https://docs.python.org/library/typing.html
.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
.. _ast.literal_eval: https://docs.python.org/library/ast.html#ast.literal_eval

Specifying multiple possible types
''''''''''''''''''''''''''''''''''

Starting from Robot Framework 4.0, it is possible to specify that an argument
has multiple possible types. In this situation argument conversion is attempted
based on each type and the whole conversion fails if none of these conversions
succeed.

When using function annotations, the natural syntax to specify that an argument
has multiple possible types is using Union_:

.. sourcecode:: python

  from typing import Union


  def example(length: Union[int, float], padding: Union[int, str, None] = None):
      ...

When using Python 3.10 or newer, it is possible to use the native `type1 | type2`__
syntax instead:

.. sourcecode:: python

  def example(length: int | float, padding: int | str | None = None):
      ...

Robot Framework 7.0 enhanced the support for the union syntax so that also
"stringly typed" unions like `'type1 | type2'` work. This syntax works also
with older Python versions:

.. sourcecode:: python

  def example(length: 'int | float', padding: 'int | str | None' = None):
      ...

An alternative is specifying types as a tuple. It is not recommended with annotations,
because that syntax is not supported by other tools, but it works well with
the `@keyword` decorator:

.. sourcecode:: python

  from robot.api.deco import keyword


  @keyword(types={'length': (int, float), 'padding': (int, str, None)})
  def example(length, padding=None):
      ...

With the above examples the `length` argument would first be converted to an
integer and if that fails then to a float. The `padding` would be first
converted to an integer, then to a string, and finally to `None`.

If the given argument has one of the accepted types, then no conversion is done
and the argument is used as-is. For example, if the `length` argument gets
value `1.5` as a float, it would not be converted to an integer. Notice that
using non-string values like floats as an argument requires using variables as
these examples giving different values to the `length` argument demonstrate:

.. sourcecode:: robotframework

   *** Test Cases ***
   Conversion
       Example    10        # Argument is a string. Converted to an integer.
       Example    1.5       # Argument is a string. Converted to a float.
       Example    ${10}     # Argument is an integer. Accepted as-is.
       Example    ${1.5}    # Argument is a float. Accepted as-is.

If one of the accepted types is string, then no conversion is done if the given
argument is a string. As the following examples giving different values to the
`padding` argument demonstrate, also in these cases passing other types is
possible using variables:

.. sourcecode:: robotframework

   *** Test Cases ***
   Conversion
       Example    1    big        # Argument is a string. Accepted as-is.
       Example    1    10         # Argument is a string. Accepted as-is.
       Example    1    ${10}      # Argument is an integer. Accepted as-is.
       Example    1    ${None}    # Argument is `None`. Accepted as-is.
       Example    1    ${1.5}     # Argument is a float. Converted to an integer.

If the given argument does not have any of the accepted types, conversion is
attempted in the order types are specified. If any conversion succeeds, the
resulting value is used without attempting remaining conversions. If no individual
conversion succeeds, the whole conversion fails.

If a specified type is not recognized by Robot Framework, then the original argument
value is used as-is. For example, with this keyword conversion would first be attempted
to an integer, but if that fails the keyword would get the original argument:

.. sourcecode:: python

  def example(argument: Union[int, Unrecognized]):
      ...

Starting from Robot Framework 6.1, the above logic works also if an unrecognized
type is listed before a recognized type like `Union[Unrecognized, int]`.
Also in this case `int` conversion is attempted, and the argument id passed as-is
if it fails. With earlier Robot Framework versions, `int` conversion would not be
attempted at all.

__ https://peps.python.org/pep-0604/
.. _Union: https://docs.python.org/3/library/typing.html#typing.Union

Type conversion with generics
'''''''''''''''''''''''''''''

With generics also the parameterized syntax like `list[int]` or `dict[str, int]`
works. When this syntax is used, the given value is first converted to the base
type and then individual items are converted to the nested types. Conversion
with different generic types works according to these rules:

- With lists there can be only one type like `list[float]`. All list items are
  converted to that type.
- With tuples there can be any number of types like `tuple[int, int]` and
  `tuple[str, int, bool]`. Tuples used as arguments are expected to have
  exactly that amount of items and they are converted to matching types.
- To create a homogeneous tuple, it is possible to use exactly one type and
  ellipsis like `tuple[int, ...]`. In this case tuple can have any number
  of items and they are all converted to the specified type.
- With dictionaries there must be exactly two types like `dict[str, int]`.
  Dictionary keys are converted using the former type and values using the latter.
- With sets there can be exactly one type like `set[float]`. Conversion logic
  is the same as with lists.

Using the native `list[int]` syntax requires `Python 3.9`__ or newer. If there
is a need to support also earlier Python versions, it is possible to either use
matching types from the typing_ module like `List[int]` or use the "stringly typed"
syntax like `'list[int]'`.

.. note:: Support for converting nested types with generics is new in
          Robot Framework 6.0. Same syntax works also with earlier versions,
          but arguments are only converted to the base type and nested types
          are not used for anything.

.. note:: Support for "stringly typed" parameterized generics is new in
          Robot Framework 7.0.

__ https://peps.python.org/pep-0585/

Custom argument converters
''''''''''''''''''''''''''

In addition to doing argument conversion automatically as explained in the
previous sections, Robot Framework supports custom argument conversion. This
functionality has two main use cases:

- Overriding the standard argument converters provided by the framework.

- Adding argument conversion for custom types and for other types not supported
  out-of-the-box.

Argument converters are functions or other callables that get arguments used
in data and convert them to desired format before arguments are passed to
keywords. Converters are registered for libraries by setting
`ROBOT_LIBRARY_CONVERTERS` attribute (case-sensitive) to a dictionary mapping
desired types to converts. When implementing a library as a module, this
attribute must be set on the module level, and with class based libraries
it must be a class attribute. With libraries implemented as classes, it is
also possible to use the `converters` argument with the `@library decorator`_.
Both of these approaches are illustrated by examples in the following sections.

.. note:: Custom argument converters are new in Robot Framework 5.0.

Overriding default converters
`````````````````````````````

Let's assume we wanted to create a keyword that accepts date_ objects for
users in Finland where the commonly used date format is `dd.mm.yyyy`.
The usage could look something like this:

.. sourcecode:: robotframework

    *** Test Cases ***
    Example
        Keyword    25.1.2022

`Automatic argument conversion`__ supports dates, but it expects them
to be in `yyyy-mm-dd` format so it will not work. A solution is creating
a custom converter and registering it to handle date_ conversion:

.. sourcecode:: python

    from datetime import date


    # Converter function.
    def parse_fi_date(value):
        day, month, year = value.split('.')
        return date(int(year), int(month), int(day))


    # Register converter function for the specified type.
    ROBOT_LIBRARY_CONVERTERS = {date: parse_fi_date}


    # Keyword using custom converter. Converter is resolved based on argument type.
    def keyword(arg: date):
        print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')


__ `Supported conversions`_

Conversion errors
`````````````````

If we try using the above keyword with invalid argument like `invalid`, it
fails with this error::

    ValueError: Argument 'arg' got value 'invalid' that cannot be converted to date: not enough values to unpack (expected 3, got 1)

This error is not too informative and does not tell anything about the expected
format. Robot Framework cannot provide more information automatically, but
the converter itself can be enhanced to validate the input. If the input is
invalid, the converter should raise a `ValueError` with an appropriate message.
In this particular case there would be several ways to validate the input, but
using `regular expressions`__ makes it possible to validate both that the input
has dots (`.`) in correct places and that date parts contain correct amount
of digits:

.. sourcecode:: python

    from datetime import date
    import re


    def parse_fi_date(value):
        # Validate input using regular expression and raise ValueError if not valid.
        match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})$', value)
        if not match:
            raise ValueError(f"Expected date in format 'dd.mm.yyyy', got '{value}'.")
        day, month, year = match.groups()
        return date(int(year), int(month), int(day))


    ROBOT_LIBRARY_CONVERTERS = {date: parse_fi_date}


    def keyword(arg: date):
        print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

With the above converter code, using the keyword with argument `invalid` fails
with a lot more helpful error message::

    ValueError: Argument 'arg' got value 'invalid' that cannot be converted to date: Expected date in format 'dd.mm.yyyy', got 'invalid'.

__ https://en.wikipedia.org/wiki/Regular_expression

Restricting value types
```````````````````````

By default Robot Framework tries to use converters with all given arguments
regardless their type. This means that if the earlier example keyword would
be used with a variable containing something else than a string, conversion
code would fail in the `re.match` call. For example, trying to use it with
argument `${42}` would fail like this::

    ValueError: Argument 'arg' got value '42' (integer) that cannot be converted to date: TypeError: expected string or bytes-like object

This error situation could naturally handled in the converter code by checking
the value type, but if the converter only accepts certain types, it is typically
easier to just restrict the value to that type. Doing it requires only adding
appropriate type hint to the converter:

.. sourcecode:: python

    def parse_fi_date(value: str):
        ...

Notice that this type hint *is not* used for converting the value before calling
the converter, it is used for strictly restricting which types can be used.
With the above addition calling the keyword with `${42}` would fail like this::

    ValueError: Argument 'arg' got value '42' (integer) that cannot be converted to date.

If the converter can accept multiple types, it is possible to specify types
as a Union_. For example, if we wanted to enhance our keyword to accept also
integers so that they would be considered seconds since the `Unix epoch`_,
we could change the converter like this:

.. sourcecode:: python

    from datetime import date
    import re
    from typing import Union


    # Accept both strings and integers.
    def parse_fi_date(value: Union[str, int]):
        # Integers are converted separately.
        if isinstance(value, int):
            return date.fromtimestamp(value)
        match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})$', value)
        if not match:
            raise ValueError(f"Expected date in format 'dd.mm.yyyy', got '{value}'.")
        day, month, year = match.groups()
        return date(int(year), int(month), int(day))


    ROBOT_LIBRARY_CONVERTERS = {date: parse_fi_date}


    def keyword(arg: date):
        print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

Converting custom types
```````````````````````

A problem with the earlier example is that date_ objects could only be given
in `dd.mm.yyyy` format. It would not work if there was a need to
support dates in different formats like in this example:

.. sourcecode:: robotframework

    *** Test Cases ***
    Example
        Finnish     25.1.2022
        US          1/25/2022
        ISO 8601    2022-01-22

A solution to this problem is creating custom types instead of overriding
the default date_ conversion:

.. sourcecode:: python

    from datetime import date
    import re
    from typing import Union

    from robot.api.deco import keyword, library


    # Custom type. Extends an existing type but that is not required.
    class FiDate(date):

        # Converter function implemented as a classmethod. It could be a normal
        # function as well, but this way all code is in the same class.
        @classmethod
        def from_string(cls, value: str):
            match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})$', value)
            if not match:
                raise ValueError(f"Expected date in format 'dd.mm.yyyy', got '{value}'.")
            day, month, year = match.groups()
            return cls(int(year), int(month), int(day))


    # Another custom type.
    class UsDate(date):

        @classmethod
        def from_string(cls, value: str):
            match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})$', value)
            if not match:
                raise ValueError(f"Expected date in format 'mm/dd/yyyy', got '{value}'.")
            month, day, year = match.groups()
            return cls(int(year), int(month), int(day))


    # Register converters using '@library' decorator.
    @library(converters={FiDate: FiDate.from_string, UsDate: UsDate.from_string})
    class Library:

        # Uses custom converter supporting 'dd.mm.yyyy' format.
        @keyword
        def finnish(self, arg: FiDate):
            print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

        # Uses custom converter supporting 'mm/dd/yyyy' format.
        @keyword
        def us(self, arg: UsDate):
            print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

        # Uses IS0-8601 compatible default conversion.
        @keyword
        def iso_8601(self, arg: date):
            print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

        # Accepts date in different formats.
        @keyword
        def any(self, arg: Union[FiDate, UsDate, date]):
            print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')


Strict type validation
``````````````````````

Converters are not used at all if the argument is of the specified type to
begin with. It is thus easy to enable strict type validation with a custom
converter that does not accept any value. For example, the :name:`Example`
keyword accepts only `StrictType` instances:

.. sourcecode:: python

    class StrictType:
        pass


    def strict_converter(arg):
        raise TypeError(f'Only StrictType instances accepted, got {type(arg).__name__}.')


    ROBOT_LIBRARY_CONVERTERS = {StrictType: strict_converter}


    def example(argument: StrictType):
        assert isinstance(argument, StrictType)

As a convenience, Robot Framework allows setting converter to `None` to get
the same effect. For example, this code behaves exactly the same way as
the code above:

.. sourcecode:: python

    class StrictType:
        pass


    ROBOT_LIBRARY_CONVERTERS = {StrictType: None}


    def example(argument: StrictType):
        assert isinstance(argument, StrictType)

.. note:: Using `None` as a strict converter is new in Robot Framework 6.0.
          An explicit converter function needs to be used with earlier versions.

Accessing the test library from converter
`````````````````````````````````````````
Starting from Robot Framework 6.1, it is possible to access the library
instance from a converter function. This allows defining dynamic type conversions
that depend on the library state. For example, if the library can be configured to
test particular locale, you might use the library state to determine how a date
should be parsed like this:

.. sourcecode:: python

    from datetime import date
    import re


    def parse_date(value, library):
        # Validate input using regular expression and raise ValueError if not valid.
        # Use locale based from library state to determine parsing format.
        if library.locale == 'en_US':
            match = re.match(r'(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})$', value)
            format = 'mm/dd/yyyy'
        else:
            match = re.match(r'(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})$', value)
            format = 'dd.mm.yyyy'
        if not match:
            raise ValueError(f"Expected date in format '{format}', got '{value}'.")
        return date(int(match.group('year')), int(match.group('month')), int(match.group('day')))


    ROBOT_LIBRARY_CONVERTERS = {date: parse_date}


    def keyword(arg: date):
        print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')


The `library` argument to converter function is optional, i.e. if the converter function
only accepts one argument, the `library` argument is omitted. Similar result can be achieved
by making the converter function accept only variadic arguments, e.g. `def parse_date(*varargs)`.

Converter documentation
```````````````````````

Information about converters is added to outputs produced by Libdoc_
automatically. This information includes the name of the type, accepted values
(if specified using type hints) and documentation. Type information is
automatically linked to all keywords using these types.

Used documentation is got from the converter function by default. If it does
not have any documentation, documentation is got from the type. Both of these
approaches to add documentation to converters in the previous example thus
produce the same result:

.. sourcecode:: python

    class FiDate(date):

        @classmethod
        def from_string(cls, value: str):
            """Date in ``dd.mm.yyyy`` format."""
            ...


    class UsDate(date):
        """Date in ``mm/dd/yyyy`` format."""

        @classmethod
        def from_string(cls, value: str):
            ...

Adding documentation is in general recommended to provide users more
information about conversion. It is especially important to document
converter functions registered for existing types, because their own
documentation is likely not very useful in this context.

`@keyword` decorator
~~~~~~~~~~~~~~~~~~~~

Although Robot Framework gets lot of information about keywords automatically,
such as their names and arguments, there are sometimes needs to configure this
information further. This is typically easiest done by using the
`robot.api.deco.keyword` decorator. It has several useful usages that are
explained thoroughly elsewhere and only listened here as a reference:

- Exposing methods and functions as keywords when the `automatic keyword
  discovery`__ has been disabled by using the `@library decorator`_ or
  otherwise.

- Setting a `custom name`__ to a keyword. This is especially useful when using
  the `embedded argument syntax`__.

- Setting `keyword tags`_.

- Setting `type information`__ to enable automatic argument type conversion.
  Supports also disabling the argument conversion altogether.

- `Marking methods to expose as keywords`_ when using the
  `dynamic library API`_ or the `hybrid library API`_.

__ `Limiting public methods becoming keywords`_
__ `Setting custom name`_
__ `Embedding arguments into keyword names`_
__ `Specifying argument types using @keyword decorator`_

`@not_keyword` decorator
~~~~~~~~~~~~~~~~~~~~~~~~

The `robot.api.deco.not_keyword` decorator can be used for
`disabling functions or methods becoming keywords`__.

__ `Using @not_keyword decorator`_

Using custom decorators
~~~~~~~~~~~~~~~~~~~~~~~

When implementing keywords, it is sometimes useful to modify them with
`Python decorators`__. However, decorators often modify function signatures
and can thus confuse Robot Framework's introspection when determining which
arguments keywords accept. This is especially problematic when creating
library documentation with Libdoc_ and when using external tools like RIDE_.
The easiest way to avoid this problem is decorating the
decorator itself using `functools.wraps`__. Other solutions include using
external modules like decorator__ and wrapt__ that allow creating fully
signature-preserving decorators.

.. note:: Support for "unwrapping" decorators decorated with `functools.wraps`
          is a new feature in Robot Framework 3.2.

__ https://realpython.com/primer-on-python-decorators/
__ https://docs.python.org/library/functools.html#functools.wraps
__ https://pypi.org/project/decorator/
__ https://wrapt.readthedocs.io

Embedding arguments into keyword names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Library keywords can also accept *embedded arguments* the same way as
`user keywords`_. This section mainly covers the Python syntax to use to
create such keywords, the embedded arguments syntax itself is covered in
detail as part of `user keyword documentation`__.

Library keywords with embedded arguments need to have a `custom name`__ that
is typically set using the `@keyword decorator`_. Values matching embedded
arguments are passed to the function or method implementing the keyword as
positional arguments. If the function or method accepts more arguments, they
can be passed to the keyword as normal positional or named arguments.
Argument names do not need to match the embedded argument names, but that
is generally a good convention.

__ `Embedding arguments into keyword name`_
__ `Setting custom name`_

Keywords accepting embedded arguments:

.. sourcecode:: python

    from robot.api.deco import keyword


    @keyword('Select ${animal} from list')
    def select_animal_from_list(animal):
        ...


    @keyword('Number of ${animals} should be')
    def number_of_animals_should_be(animals, count):
        ...

Tests using the above keywords:

.. sourcecode:: robotframework

    *** Test Cases ***
    Embedded arguments
        Select cat from list
        Select dog from list

    Embedded and normal arguments
        Number of cats should be    2
        Number of dogs should be    count=3

If type information is specified, automatic `argument conversion`_ works also
with embedded arguments:

.. sourcecode:: python

    @keyword('Add ${quantity} copies of ${item} to cart')
    def add_copies_to_cart(quantity: int, item: str):
        ...

.. note:: Support for mixing embedded arguments and normal arguments is new
          in Robot Framework 7.0.

Asynchronous keywords
~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 6.1, it is possible to run native asynchronous
functions (created by `async def`) just like normal functions:

.. sourcecode:: python

    import asyncio
    from robot.api.deco import keyword


    @keyword
    async def this_keyword_waits():
        await asyncio.sleep(5)

You can get the reference of the loop using `asyncio.get_running_loop()` or
`asyncio.get_event_loop()`. Be careful when modifying how the loop runs, it is
a global resource. For example, never call `loop.close()` because it will make it
impossible to run any further coroutines. If you have any function or resource that
requires the event loop, even though `await` is not used explicitly, you have to define
your function as async to have the event loop available.

More examples of functionality:

.. sourcecode:: python

    import asyncio
    from robot.api.deco import keyword


    async def task_async():
        await asyncio.sleep(5)

    @keyword
    async def examples():
        tasks = [task_async() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        background_task = asyncio.create_task(task_async())
        await background_task

        # If running with Python 3.10 or higher
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(task_async())
            task2 = tg.create_task(task_async())

.. note:: Robot Framework waits for the function to complete. If you want to have a task that runs
          for a long time, use, for example, `asyncio.create_task()`. It is your responsibility to
          manage the task and save a reference to avoid it being garbage collected. If the event loop
          closes and a task is still pending, a message will be printed to the console.

.. note:: If execution of keyword cannot continue for some reason, for example a signal stop,
          Robot Framework will cancel the async task and any of its children. Other async tasks will
          continue running normally.

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

Normal execution failures and errors can be reported using the standard exceptions
such as `AssertionError`, `ValueError` and `RuntimeError`. There are, however, some
special cases explained in the subsequent sections where special exceptions are needed.

Error messages
''''''''''''''

The error message shown in logs, reports and the console is created
from the exception type and its message. With generic exceptions (for
example, `AssertionError`, `Exception`, and
`RuntimeError`), only the exception message is used, and with
others, the message is created in the format `ExceptionType:
Actual message`.

It is possible to avoid adding the
exception type as a prefix to failure message also with non generic exceptions.
This is done by adding a special `ROBOT_SUPPRESS_NAME` attribute with
value `True` to your exception.

Python:

.. sourcecode:: python

    class MyError(RuntimeError):
        ROBOT_SUPPRESS_NAME = True

In all cases, it is important for the users that the exception message is as
informative as possible.

HTML in error messages
''''''''''''''''''''''

It is also possible to have HTML formatted
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

Exceptions provided by Robot Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework provides some exceptions that libraries can use for reporting
failures and other events. These exceptions are exposed via the `robot.api`__
package and contain the following:

`Failure`
    Report failed validation. There is no practical difference in using this exception
    compared to using the standard `AssertionError`. The main benefit of using this
    exception is that its name is consistent with other provided exceptions.

`Error`
    Report error in execution. Failures related to the system not behaving as expected
    should typically be reported using the `Failure` exception or the standard
    `AssertionError`. This exception can be used, for example, if the keyword is used
    incorrectly. There is no practical difference, other than consistent naming with
    other provided exceptions, compared to using this exception and the standard
    `RuntimeError`.

`ContinuableFailure`
    Report failed validation but allow continuing execution.
    See the `Continuable failures`_ section below for more information.

`SkipExecution`
    Mark the executed test or task skipped_.
    See the `Skipping tests`_ section below for more information.

`FatalError`
    Report error that stops the whole execution.
    See the `Stopping test execution`_ section below for more information.

__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.api.html

.. note:: All these exceptions are new in Robot Framework 4.0. Other features than
          skipping tests, which is also new in Robot Framework 4.0, are available
          by other means in earlier versions.

Continuable failures
~~~~~~~~~~~~~~~~~~~~

It is possible to `continue test execution even when there are failures`__.
The easiest way to do that is using the provided__ `robot.api.ContinuableFailure`
exception:

.. sourcecode:: python

    from robot.api import ContinuableFailure


    def example_keyword():
        if something_is_wrong():
            raise ContinuableFailure('Something is wrong but execution can continue.')
        ...

An alternative is creating a custom exception that has a special
`ROBOT_CONTINUE_ON_FAILURE` attribute set to a `True` value.
This is demonstrated by the example below.

.. sourcecode:: python

    class MyContinuableError(RuntimeError):
        ROBOT_CONTINUE_ON_FAILURE = True

__ `Continue on failure`_
__ `Exceptions provided by Robot Framework`_

Skipping tests
~~~~~~~~~~~~~~

It is possible to skip_ tests with a library keyword. The easiest way to
do that is using the provided__ `robot.api.SkipExecution` exception:

.. sourcecode:: python

    from robot.api import SkipExecution


    def example_keyword():
        if test_should_be_skipped():
            raise SkipExecution('Cannot proceed, skipping test.')
        ...

An alternative is creating a custom exception that has a special
`ROBOT_SKIP_EXECUTION` attribute set to a `True` value.
This is demonstrated by the example below.

.. sourcecode:: python

    class MySkippingError(RuntimeError):
        ROBOT_SKIP_EXECUTION = True

__ `Exceptions provided by Robot Framework`_

Stopping test execution
~~~~~~~~~~~~~~~~~~~~~~~

It is possible to fail a test case so that `the whole test execution is
stopped`__. The easiest way to accomplish this is using the provided__
`robot.api.FatalError` exception:

.. sourcecode:: python

    from robot.api import FatalError


    def example_keyword():
        if system_is_not_running():
            raise FatalError('System is not running!')
        ...

In addition to using the `robot.api.FatalError` exception, it is possible create
a custom exception that has a special `ROBOT_EXIT_ON_FAILURE` attribute set to
a `True` value. This is illustrated by the example below.

.. sourcecode:: python

    class MyFatalError(RuntimeError):
        ROBOT_EXIT_ON_FAILURE = True


__ `Stopping test execution gracefully`_
__ `Exceptions provided by Robot Framework`_

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
the message in the format `*LEVEL* Actual log message`.
In this formant `*LEVEL*` must be in the beginning of a line and `LEVEL`
must be one of the available concrete log levels `TRACE`, `DEBUG`,
`INFO`, `WARN` or `ERROR`, or a pseudo log level `HTML` or `CONSOLE`.
The pseudo levels can be used for `logging HTML`_ and `logging to console`_,
respectively.

Errors and warnings
'''''''''''''''''''

Messages with `ERROR` or `WARN` level are automatically written to the
console and a separate `Test Execution Errors section`__ in the log
files. This makes these messages more visible than others and allows
using them for reporting important but non-critical problems to users.

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
since the `Unix epoch`_ and it must be placed after the `log level`__
separated from it with a colon::

   *INFO:1308435758660* Message with timestamp
   *HTML:1308435758661* <b>HTML</b> message with timestamp

As illustrated by the examples below, adding the timestamp is easy.
It is, however, even easier to get accurate timestamps using the
`programmatic logging APIs`_. A big benefit of adding timestamps explicitly
is that this approach works also with the `remote library interface`_.

.. sourcecode:: python

    import time


    def example_keyword():
        timestamp = int(time.time() * 1000)
        print(f'*INFO:{timestamp}* Message with timestamp')

.. _Unix epoch: http://en.wikipedia.org/wiki/Unix_time
__ `Using log levels`_

Logging to console
''''''''''''''''''

Libraries have several options for writing messages to the console.
As already discussed, warnings and all messages written to the
standard error stream are written both to the log file and to the
console. Both of these options have a limitation that the messages end
up to the console only after the currently executing keyword finishes.

Starting from Robot Framework 6.1, libraries can use a pseudo log level
`CONSOLE` for logging messages *both* to the log file and to the console:

.. sourcecode:: python

   def my_keyword(arg):
       print('*CONSOLE* Message both to log and to console.')

These messages will be logged to the log file using the `INFO` level similarly
as with the `HTML` pseudo log level. When using this approach, messages
are logged to the console only after the keyword execution ends.

Another option is writing messages to `sys.__stdout__` or `sys.__stderr__`.
When using this approach, messages are written to the console immediately
and are not written to the log file at all:

.. sourcecode:: python

   import sys


   def my_keyword(arg):
       print('Message only to console.', file=sys.__stdout__)

The final option is using the `public logging API`_. Also in with this approach
messages are written to the console immediately:

.. sourcecode:: python

   from robot.api import logger


   def log_to_console(arg):
       logger.console('Message only to console.')

   def log_to_console_and_log_file(arg):
       logger.info('Message both to log and to console.', also_console=True)

Logging example
'''''''''''''''

In most cases, the `INFO` level is adequate. The levels below it,
`DEBUG` and `TRACE`, are useful for writing debug information.
These messages are normally not shown, but they can facilitate debugging
possible problems in the library itself. The `WARN` or `ERROR` level can
be used to make messages more visible and `HTML` is useful if any
kind of formatting is needed. Level `CONSOLE` can be used when the
message needs to shown both in console and in the log file.

The following examples clarify how logging with different levels
works.

.. sourcecode:: python

   print('Hello from a library.')
   print('*WARN* Warning from a library.')
   print('*ERROR* Something unexpected happen that may indicate a problem in the test.')
   print('*INFO* Hello again!')
   print('This will be part of the previous message.')
   print('*INFO* This is a new message.')
   print('*INFO* This is <b>normal text</b>.')
   print('*CONSOLE* This logs into console and log file.')
   print('*HTML* This is <b>bold</b>.')
   print('*HTML* <a href="http://robotframework.org">Robot Framework</a>')

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
       <td class="msg">This logs into console and log file.</td>
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
using the standard output and error streams.

Public logging API
''''''''''''''''''

Robot Framework has a Python based logging API for writing
messages to the log file and to the console. Test libraries can use
this API like `logger.info('My message')` instead of logging
through the standard output like `print('*INFO* My message')`. In
addition to a programmatic interface being a lot cleaner to use, this
API has a benefit that the log messages have accurate timestamps_.

The public logging API `is thoroughly documented`__ as part of the API
documentation at https://robot-framework.readthedocs.org. Below is
a simple usage example:

.. sourcecode:: python

   from robot.api import logger


   def my_keyword(arg):
       logger.debug(f"Got argument '{arg}'.")
       do_something()
       logger.info('<i>This</i> is a boring example', html=True)
       logger.console('Hello, console!')

An obvious limitation is that test libraries using this logging API have
a dependency to Robot Framework. If Robot Framework is not running,
the messages are redirected automatically to Python's standard logging__
module.

__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.api.html#module-robot.api.logger
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
       logging.debug(f"Got argument '{arg}'.")
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

Library logging using the logging API during import:

.. sourcecode:: python

   from robot.api import logger


   logger.debug("Importing library")


   def keyword():
       ...

.. note:: If you log something during initialization, i.e. in Python
          `__init__`, the messages may be
          logged multiple times depending on the `library scope`_.

__ `Logging information`_

Returning values
~~~~~~~~~~~~~~~~

The final way for keywords to communicate back to the core framework
is returning information retrieved from the system under test or
generated by some other means. The returned values can be `assigned to
variables`__ in the test data and then used as inputs for other keywords,
even from different test libraries.

Values are returned using the `return` statement in methods. Normally,
one value is assigned into one `scalar variable`__, as illustrated in
the example below. This example
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
that returned values are lists or list-like objects.

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

Detecting is Robot Framework running
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 6.1, it is easy to detect is Robot Framework
running at all and is the dry-run mode active by using the `robot_running`
and `dry_run_active` properties of the BuiltIn library. A relatively common
use case is that library initializers may want to avoid doing some work if
the library is not used during execution but is initialized, for example,
by Libdoc_:

.. sourcecode:: python

   from robot.libraries.BuiltIn import BuiltIn


   class MyLibrary:

       def __init__(self):
           builtin = BuiltIn()
           if builtin.robot_running and not builtin.dry_run_active:
               # Do some initialization that only makes sense during real execution.

For more information about using the BuiltIn library as a programmatic API,
including another example using `robot_running`, see the `Using BuiltIn library`_
section.

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
means using docstrings_ as in the example below.

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

Python has tools for creating an API documentation of a
library documented as above. However, outputs from these tools can be slightly
technical for some users. Another alternative is using Robot
Framework's own documentation tool Libdoc_. This tool can
create a library documentation from libraries
using the static library API, such as the ones above, but it also handles
libraries using the `dynamic library API`_ and `hybrid library API`_.

The first logical line of a keyword documentation, until the first empty line,
is used for a special purpose and should contain a short overall description
of the keyword. It is used as a *short documentation* by Libdoc_ (for example,
as a tool tip) and also shown in the `test logs`_.

By default documentation is considered to follow Robot Framework's
`documentation formatting`_ rules. This simple format allows often used
styles like `*bold*` and `_italic_`, tables, lists, links, etc.
It is possible to use also HTML, plain
text and reStructuredText_ formats. See the `Documentation format`_
section for information how to set the format in the library source code and
Libdoc_ chapter for more information about the formats in general.

.. note:: Prior to Robot Framework 3.1, the short documentation contained
          only the first physical line of the keyword documentation.

.. _docstrings: http://www.python.org/dev/peps/pep-0257

Testing libraries
~~~~~~~~~~~~~~~~~

Any non-trivial test library needs to be thoroughly tested to prevent
bugs in them. Of course, this testing should be automated to make it
easy to rerun tests when libraries are changed.

Python has excellent unit testing tools, and they suite
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
using normal packaging tools. For information about packaging and
distributing Python code see https://packaging.python.org/. When such
a package is installed using pip_ or other tools, it is automatically
in the `module search path`_.

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
`user keywords`__.

__ `Errors and warnings during execution`_
__ `Documenting libraries`_
__ `User keyword name and documentation`_

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
done using reflection, but dynamic libraries have special methods
that are used for these purposes.

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
possible.
Python users may also find the PythonLibCore__ project useful.

__ https://github.com/robotframework/PythonLibCore

.. _`Getting dynamic keyword names`:

Getting keyword names
~~~~~~~~~~~~~~~~~~~~~

Dynamic libraries tell what keywords they implement with the
`get_keyword_names` method. This
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
creates a `custom 'robot_name' attribute`__ on the decorated method.
This allows generating the list of keywords just by checking for the `robot_name`
attribute on every method in the library during `get_keyword_names`.

.. sourcecode:: python

   from robot.api.deco import keyword


   class DynamicExample:

       def get_keyword_names(self):
           # Get all attributes and their values from the library.
           attributes = [(name, getattr(self, name)) for name in dir(self)]
           # Filter out attributes that do not have 'robot_name' set.
           keywords = [(name, value) for name, value in attributes
                       if hasattr(value, 'robot_name')]
           # Return value of 'robot_name', if given, or the original 'name'.
           return [value.robot_name or name for name, value in keywords]

       def helper_method(self):
           ...

       @keyword
       def keyword_method(self):
           ...

__ `Setting custom name`_

.. _`Running dynamic keywords`:

Running keywords
~~~~~~~~~~~~~~~~

Dynamic libraries have a special `run_keyword` (alias `runKeyword`)
method for executing their keywords. When a keyword from a dynamic
library is used in the test data, Robot Framework uses the `run_keyword`
method to get it executed. This method takes two or three arguments.
The first argument is a string containing the name of the keyword to be
executed in the same format as returned by `get_keyword_names`. The second
argument is a list of `positional arguments`_ given to the keyword in
the test data, and the optional third argument is a dictionary
containing `named arguments`_. If the third argument is missing, `free named
arguments`__ and `named-only arguments`__ are not supported, and other
named arguments are mapped to positional arguments.

.. note:: Prior to Robot Framework 3.1, normal named arguments were
          mapped to positional arguments regardless did `run_keyword`
          accept two or three arguments. The third argument only got
          possible free named arguments.

After getting keyword name and arguments, the library can execute
the keyword freely, but it must use the same mechanism to
communicate with the framework as static libraries. This means using
exceptions for reporting keyword status, logging by writing to
the standard output or by using the provided logging APIs, and using
the return statement in `run_keyword` for returning something.

Every dynamic library must have both the `get_keyword_names` and
`run_keyword` methods but rest of the methods in the dynamic
API are optional. The example below shows a working, albeit
trivial, dynamic library.

.. sourcecode:: python

   class DynamicExample:

       def get_keyword_names(self):
           return ['first keyword', 'second keyword']

       def run_keyword(self, name, args, named_args):
           print(f"Running keyword '{name}' with positional arguments {args} "
                 f"and named arguments {named_args}.")

__ `Free named arguments with dynamic libraries`_
__ `Named-only arguments with dynamic libraries`_

Getting keyword arguments
~~~~~~~~~~~~~~~~~~~~~~~~~

If a dynamic library only implements the `get_keyword_names` and
`run_keyword` methods, Robot Framework does not have any information
about the arguments that the implemented keywords accept. For example,
both :name:`First Keyword` and :name:`Second Keyword` in the example above
could be used with any arguments. This is problematic,
because most real keywords expect a certain number of keywords, and
under these circumstances they would need to check the argument counts
themselves.

Dynamic libraries can communicate what arguments their keywords expect
by using the `get_keyword_arguments` (alias `getKeywordArguments`) method.
This method gets the name of a keyword as an argument, and it must return
a list of strings containing the arguments accepted by that keyword.

Similarly as other keywords, dynamic keywords can require any number
of `positional arguments`_, have `default values`_, accept `variable number of
arguments`_, accept `free named arguments`_ and have `named-only arguments`_.
The syntax how to represent all these different variables is derived from how
they are specified in Python and explained in the following table.

.. table:: Representing different arguments with `get_keyword_arguments`
   :class: tabular

   +--------------------+----------------------------+------------------------------+
   |   Argument type    |      How to represent      |          Examples            |
   +====================+============================+==============================+
   | No arguments       | Empty list.                | | `[]`                       |
   +--------------------+----------------------------+------------------------------+
   | One or more        | List of strings containing | | `['argument']`             |
   | `positional        | argument names.            | | `['arg1', 'arg2', 'arg3']` |
   | argument`_         |                            |                              |
   +--------------------+----------------------------+------------------------------+
   | `Default values`_  | Two ways how to represent  | String with `=` separator:   |
   |                    | the argument name and the  |                              |
   |                    | default value:             | | `['name=default']`         |
   |                    |                            | | `['a', 'b=1', 'c=2']`      |
   |                    | - As a string where the    |                              |
   |                    |   name and the default are | Tuple:                       |
   |                    |   separated with `=`.      |                              |
   |                    | - As a tuple with the name | | `[('name', 'default')]`    |
   |                    |   and the default as       | | `['a', ('b', 1), ('c', 2)]`|
   |                    |   separate items. New in   |                              |
   |                    |   Robot Framework 3.2.     |                              |
   +--------------------+----------------------------+------------------------------+
   | `Positional-only   | Arguments before the `/`   | | `['posonly', '/']`         |
   | arguments`_        | marker. New in Robot       | | `['p', 'q', '/', 'normal']`|
   |                    | Framework 6.1.             |                              |
   +--------------------+----------------------------+------------------------------+
   | `Variable number   | Argument after possible    | | `['*varargs']`             |
   | of arguments`_     | positional arguments has   | | `['argument', '*rest']`    |
   | (varargs)          | a `*` prefix               | | `['a', 'b=42', '*c']`      |
   +--------------------+----------------------------+------------------------------+
   | `Named-only        | Arguments after varargs or | | `['*varargs', 'named']`    |
   | arguments`_        | a lone `*` if there are no | | `['*', 'named']`           |
   |                    | varargs. With or without   | | `['*', 'x', 'y=default']`  |
   |                    | defaults. Requires         | | `['a', '*b', ('c', 42)]`   |
   |                    | `run_keyword` to `support  |                              |
   |                    | named-only arguments`__.   |                              |
   |                    | New in Robot Framework 3.1.|                              |
   +--------------------+----------------------------+------------------------------+
   | `Free named        | Last arguments has `**`    | | `['**named']`              |
   | arguments`_        | prefix. Requires           | | `['a', ('b', 42), '**c']`  |
   | (kwargs)           | `run_keyword` to `support  | | `['*varargs', '**kwargs']` |
   |                    | free named arguments`__.   | | `['*', 'kwo', '**kws']`    |
   +--------------------+----------------------------+------------------------------+

When the `get_keyword_arguments` is used, Robot Framework automatically
calculates how many positional arguments the keyword requires and does it
support free named arguments or not. If a keyword is used with invalid
arguments, an error occurs and `run_keyword` is not even called.

The actual argument names and default values that are returned are also
important. They are needed for `named argument support`__ and the Libdoc_
tool needs them to be able to create a meaningful library documentation.

As explained in the above table, default values can be specified with argument
names either as a string like `'name=default'` or as a tuple like
`('name', 'default')`. The main problem with the former syntax is that all
default values are considered strings whereas the latter syntax allows using
all objects like `('inteter', 1)` or `('boolean', True)`. When using other
objects than strings, Robot Framework can do `automatic argument conversion`__
based on them.

For consistency reasons, also arguments that do not accept default values can
be specified as one item tuples. For example, `['a', 'b=c', '*d']` and
`[('a',), ('b', 'c'), ('*d',)]` are equivalent.

If `get_keyword_arguments` is missing or returns Python `None` for a certain
keyword, that keyword gets an argument specification
accepting all arguments. This automatic argument spec is either
`[*varargs, **kwargs]` or `[*varargs]`, depending does
`run_keyword` `support free named arguments`__ or not.

.. note:: Support to specify arguments as tuples like `('name', 'default')`
          is new in Robot Framework 3.2. Support for positional-only arguments
          in dynamic library API is new in Robot Framework 6.1.

__ `Free named arguments with dynamic libraries`_
__ `Named-only arguments with dynamic libraries`_
__ `Named argument syntax with dynamic libraries`_
__ `Implicit argument types based on default values`_
__ `Free named arguments with dynamic libraries`_

Getting keyword argument types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework 3.1 introduced support for automatic argument conversion
and the dynamic library API supports that as well. The conversion logic
works exactly like with `static libraries`__, but how the type information
is specified is naturally different.

With dynamic libraries types can be returned using the optional
`get_keyword_types` method (alias `getKeywordTypes`). It can return types
using a list or a dictionary exactly like types can be specified when using
the `@keyword decorator`__. Type information can be specified using actual
types like `int`, but especially if a dynamic library gets this information
from external systems, using strings like `'int'` or `'integer'` may be
easier. See the `Supported conversions`_ section for more information about
supported types and how to specify them.

Robot Framework does automatic argument conversion also based on the
`argument default values`__. Earlier this did not work with the dynamic API
because it was possible to specify arguments only as strings. As
`discussed in the previous section`__, this was changed in Robot Framework
3.2 and nowadays default values returned like `('example', True)` are
automatically used for this purpose.

Starting from Robot Framework 7.0, dynamic libraries can also specify the
keyword return type by using key `'return'` with an appropriate type in the
returned type dictionary. This information is not used for anything during
execution, but it is shown by Libdoc_ for documentation purposes.

__ `Argument conversion`_
__ `Specifying argument types using @keyword decorator`_
__ `Implicit argument types based on default values`_
__ `Getting keyword arguments`_

Getting keyword tags
~~~~~~~~~~~~~~~~~~~~

Dynamic libraries can report `keyword
tags`_ by using the `get_keyword_tags` method (alias `getKeywordTags`). It
gets a keyword name as an argument, and should return corresponding tags
as a list of strings.

Alternatively it is possible to specify tags on the last row of the
documentation returned by the `get_keyword_documentation` method discussed
below. This requires starting the last row with `Tags:` and listing tags
after it like `Tags: first tag, second, third`.

.. tip:: The `get_keyword_tags` method is guaranteed to be called before
         the `get_keyword_documentation` method. This makes it easy to
         embed tags into the documentation only if the `get_keyword_tags`
         method is not called.

Getting keyword documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If dynamic libraries want to provide keyword documentation, they can implement
the `get_keyword_documentation` method (alias `getKeywordDocumentation`). It
takes a keyword name as an argument and, as the method name implies, returns
its documentation as a string.

The returned documentation is used similarly as the keyword
documentation string with static libraries.
The main use case is getting keywords' documentations into a
library documentation generated by Libdoc_. Additionally,
the first line of the documentation (until the first `\n`) is
shown in test logs.

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

Dynamic libraries can also specify the general library
documentation directly in the code as the docstring of the library
class and its `__init__` method. If a non-empty documentation is
got both directly from the code and from the
`get_keyword_documentation` method, the latter has precedence.

Getting keyword source information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The dynamic API masks the real implementation of keywords from Robot Framework
and thus makes it impossible to see where keywords are implemented. This
means that editors and other tools utilizing Robot Framework APIs cannot
implement features such as go-to-definition. This problem can be solved by
implementing yet another optional dynamic method named `get_keyword_source`
(alias `getKeywordSource`) that returns the source information.

The return value from the `get_keyword_source` method must be a string or
`None` if no source information is available. In the simple
case it is enough to simply return an absolute path to the file implementing
the keyword. If the line number where the keyword implementation starts
is known, it can be embedded to the return value like `path:lineno`.
Returning only the line number is possible like `:lineno`.

The source information of the library itself is got automatically from
the imported library class the same way as with other library APIs. The
library source path is used with all keywords that do not have their own
source path defined.

.. note:: Returning source information for keywords is a new feature in
          Robot Framework 3.2.

Named argument syntax with dynamic libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Also the dynamic library API supports
the `named argument syntax`_. Using the syntax works based on the
argument names and default values `got from the library`__ using the
`get_keyword_arguments` method.


If the `run_keyword` method accepts three arguments, the second argument
gets all positional arguments as a list and the last arguments gets all
named arguments as a mapping. If it accepts only two arguments, named
arguments are mapped to positional arguments. In the latter case, if
a keyword has multiple arguments with default values and only some of
the latter ones are given, the framework fills the skipped optional
arguments based on the default values returned by the `get_keyword_arguments`
method.

Using the named argument syntax with dynamic libraries is illustrated
by the following examples. All the examples use a keyword :name:`Dynamic`
that has an argument specification `[a, b=d1, c=d2]`. The comment on each row
shows how `run_keyword` would be called in these cases if it has two arguments
(i.e. signature is `name, args`) and if it has three arguments (i.e.
`name, args, kwargs`).

.. sourcecode:: robotframework

   *** Test Cases ***                  # args          # args, kwargs
   Positional only
       Dynamic    x                    # [x]           # [x], {}
       Dynamic    x      y             # [x, y]        # [x, y], {}
       Dynamic    x      y      z      # [x, y, z]     # [x, y, z], {}

   Named only
       Dynamic    a=x                  # [x]           # [], {a: x}
       Dynamic    c=z    a=x    b=y    # [x, y, z]     # [], {a: x, b: y, c: z}

   Positional and named
       Dynamic    x      b=y           # [x, y]        # [x], {b: y}
       Dynamic    x      y      c=z    # [x, y, z]     # [x, y], {c: z}
       Dynamic    x      b=y    c=z    # [x, y, z]     # [x], {y: b, c: z}

   Intermediate missing
       Dynamic    x      c=z           # [x, d1, z]    # [x], {c: z}

.. note:: Prior to Robot Framework 3.1, all normal named arguments were
          mapped to positional arguments and the optional `kwargs` was
          only used with free named arguments. With the above examples
          `run_keyword` was always called like it is nowadays called if
          it does not support `kwargs`.

__ `Getting keyword arguments`_

Free named arguments with dynamic libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic libraries can also support
`free named arguments`_ (`**named`). A mandatory precondition for
this support is that the `run_keyword` method `takes three arguments`__:
the third one will get the free named arguments along with possible other
named arguments. These arguments are passed to the keyword as a mapping.

What arguments a keyword accepts depends on what `get_keyword_arguments`
`returns for it`__. If the last argument starts with `**`, that keyword is
recognized to accept free named arguments.

Using the free named argument syntax with dynamic libraries is illustrated
by the following examples. All the examples use a keyword :name:`Dynamic`
that has an argument specification `[a=d1, b=d2, **named]`. The comment shows
the arguments that the `run_keyword` method is actually called with.

.. sourcecode:: robotframework

   *** Test Cases ***                  # args, kwargs
   No arguments
       Dynamic                         # [], {}

   Only positional
       Dynamic    x                    # [x], {}
       Dynamic    x      y             # [x, y], {}

   Only free named
       Dynamic    x=1                  # [], {x: 1}
       Dynamic    x=1    y=2    z=3    # [], {x: 1, y: 2, z: 3}

   Positional and free named
       Dynamic    x      y=2           # [x], {y: 2}
       Dynamic    x      y=2    z=3    # [x], {y: 2, z: 3}

   Positional as named and free named
       Dynamic    a=1    x=1           # [], {a: 1, x: 1}
       Dynamic    b=2    x=1    a=1    # [], {a: 1, b: 2, x: 1}

.. note:: Prior to Robot Framework 3.1, normal named arguments were mapped
          to positional arguments but nowadays they are part of the
          `kwargs` along with the free named arguments.

__ `Running dynamic keywords`_
__ `Getting keyword arguments`_

Named-only arguments with dynamic libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 3.1, dynamic libraries can have `named-only
arguments`_. This requires that the `run_keyword` method `takes three
arguments`__: the third getting the named-only arguments along with the other
named arguments.

In the `argument specification`__ returned by the `get_keyword_arguments`
method named-only arguments are specified after possible variable number
of arguments (`*varargs`) or a lone asterisk (`*`) if the keyword does not
accept varargs. Named-only arguments can have default values, and the order
of arguments with and without default values does not matter.

Using the named-only argument syntax with dynamic libraries is illustrated
by the following examples. All the examples use a keyword :name:`Dynamic`
that has been specified to have argument specification
`[positional=default, *varargs, named, named2=default, **free]`. The comment
shows the arguments that the `run_keyword` method is actually called with.

.. sourcecode:: robotframework

   *** Test Cases ***                                  # args, kwargs
   Only named-only
       Dynamic    named=value                          # [], {named: value}
       Dynamic    named=value    named2=2              # [], {named: value, named2: 2}

   Named-only with positional and varargs
       Dynamic    argument       named=xxx             # [argument], {named: xxx}
       Dynamic    a1             a2         named=3    # [a1, a2], {named: 3}

   Named-only with positional as named
       Dynamic    named=foo      positional=bar        # [], {positional: bar, named: foo}

   Named-only with free named
       Dynamic    named=value    foo=bar               # [], {named: value, foo=bar}
       Dynamic    named2=2       third=3    named=1    # [], {named: 1, named2: 2, third: 3}

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
   `get_keyword_arguments`      `name`                     Return keywords' `argument specification`__. Optional method.
   `get_keyword_types`          `name`                     Return keywords' `argument type information`__. Optional method. New in RF 3.1.
   `get_keyword_tags`           `name`                     Return keywords' `tags`__. Optional method.
   `get_keyword_documentation`  `name`                     Return keywords' and library's `documentation`__. Optional method.
   `get_keyword_source`         `name`                     Return keywords' `source`__. Optional method. New in RF 3.2.
   ===========================  =========================  =======================================================

__ `Getting dynamic keyword names`_
__ `Running dynamic keywords`_
__ `Getting keyword arguments`_
__ `Getting keyword argument types`_
__ `Getting keyword tags`_
__ `Getting keyword documentation`_
__ `Getting keyword source information`_

A good example of using the dynamic API is Robot Framework's own
`Remote library`_.

.. note:: Starting from Robot Framework 7.0, dynamic libraries can have asynchronous
          implementations of their special methods.

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
           print(f"My Keyword called with '{args}'.")

       def __getattr__(self, name):
           if name == 'external_keyword':
               return external_keyword
           raise AttributeError(f"Non-existing attribute '{name}'.")

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

When implementing a test library, the hybrid API has the same
dynamic capabilities as the actual dynamic API. A great benefit with it is
that there is no need to have special methods for getting keyword
arguments and documentation. It is also often practical that the only real
dynamic keywords need to be handled in `__getattr__` and others
can be implemented directly in the main library class.

Because of the clear benefits and equal capabilities, the hybrid API
is in most cases a better alternative than the dynamic API.
One notable exception is implementing a library as a proxy for
an actual library implementation elsewhere, because then the actual
keyword must be executed elsewhere and the proxy can only pass forward
the keyword name and arguments.

A good example of using the hybrid API is Robot Framework's own
Telnet_ library.

Using Robot Framework's internal modules
----------------------------------------

Test libraries can use Robot Framework's
internal modules, for example, to get information about the executed
tests and the settings that are used. This powerful mechanism to
communicate with the framework should be used with care, though,
because all Robot Framework's APIs are not meant to be used by
externally and they might change radically between different framework
versions.

Available APIs
~~~~~~~~~~~~~~

`API documentation`_ is hosted separately
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
       builtin = BuiltIn()
       output = do_something_that_creates_a_lot_of_output(argument)
       if builtin.robot_running:
           output_dir = builtin.replace_variables('${OUTPUT_DIR}')
       else:
           output_dir = '.'
       with open(os.path.join(output_dir, 'output.txt'), 'w') as file:
           file.write(output)
       print('*HTML* Output written to <a href="output.txt">output.txt</a>')

As the above examples illustrates, BuiltIn also has a convenient `robot_running`
property for `detecting is Robot Framework running`_.

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
:name:`Title Should Start With` keyword to the SeleniumLibrary_.

.. sourcecode:: python

   from robot.api.deco import keyword
   from SeleniumLibrary import SeleniumLibrary


   class ExtendedSeleniumLibrary(SeleniumLibrary):

       @keyword
       def title_should_start_with(self, expected):
           title = self.get_title()
           if not title.startswith(expected):
               raise AssertionError(f"Title '{title}' did not start with '{expected}'.")

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
           raise AssertionError(f"Title '{title}' did not start with '{expected}'.")

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
