.. include:: <isonum.txt>

Python Tutorial for Robot Framework Test Library Developers
===========================================================

| Copyright |copy| Nokia Siemens Networks 2009
| Licensed under the `Creative Commons Attribution 3.0 Unported`__ license

__ http://creativecommons.org/licenses/by/3.0/

.. contents:: Table of Contents
   :depth: 2

Introduction
------------

* This is self learning material for `Python language`_. The target is
  to learn enough Python to be able to start creating test
  libraries for `Robot Framework`_.

* Earlier programming experience is expected but not absolutely
  necessary.

* The main study material for this training is *Dive Into Python* book
  which is really good and freely available for on-line reading,
  downloading or printing from http://diveintopython.org.  It is
  targeted for people who already know how to program but do not know
  Python before.

* If you are a novice programmer, it might better to start with `Think
  Python`_ book. It is also available for free and its target audience
  is people without any earlier programming knowledge.

* `Python Tutorial`_, available at http://python.org and included into
  the standard Python installation at least on Windows, is also
  good. Some of the sections in this training refer to it instead of
  or in addition to Dive Into Python.

* The official Python website at http://python.org is a good place to
  search for more documentation and Python related information in
  general.

* If you need information about Jython, the Java implementation of
  Python, you can start from http://jython.org.

.. _Python language: http://python.org
.. _Robot Framework: http://robotframework.org
.. _Think Python: http://www.greenteapress.com/thinkpython/thinkpython.html
.. _Python Tutorial: http://docs.python.org/tut/tut.html


Getting started
---------------

Installation
''''''''''''

* Most Linux distributions, OS X, and other UNIX like machines have
  Python installed automatically, but on Windows you probably need to
  install it separately. Installers for different platforms can be
  found from http://python.org.

* Robot Framework does not yet support Python 3.x and also this
  tutorial is based on Python 2.x. Any 2.x version up from 2.3 is
  sufficient but the latest versions are recommended.

* It is highly recommended that you configure your system so that you
  can run Python from command line simply by typing ``python`` and pressing
  enter.

   - On Windows, and possibly on some other systems, this requires
     adding Python installation directory into PATH environment
     variable. For more information and instructions on how to do it
     see `Robot Framework user guide`_.

.. _Robot Framework user guide: http://robotframework.googlecode.com/svn/tags/robotframework-2.1/doc/userguide/RobotFrameworkUserGuide.html#setting-up-environment


Interactive interpreter
'''''''''''''''''''''''

* Start from command line by typing ``python``. On Windows you can
  also start it from ``Start > All Programs > Python 2.x``.

* Statements and expressions can be written in the console. Pressing <Enter>
  will interpret the line and any possible results are echoed. Try for example:

  .. sourcecode:: pycon

    >>> 1+2
    3

* To exit press first ``Ctrl-Z`` and then enter on Windows and
  ``Ctrl-D`` on other systems.

  - With Python 2.5 and newer you can exit the interpreter also with
    command ``exit()``.

* `Dive Into Python`__ has some more examples.

.. __: http://diveintopython.org/installing_python/shell.html


Python editors
''''''''''''''

* Most general purpose text editors (Emacs, VIM, UltraEdit, ...) and
  IDEs (Eclipse, Netbeans, ...) can be used to edit Python. There are
  also some editors specially for Python.

* The most important editor features are source highlighting and
  handling indentation. Make sure your editor of choise supports them
  either natively or via Python plugin or mode.

* If you don't know any editor, you can at least get started with
  `IDLE`_.  It is included in the standard Python installation on
  Windows and can be installed also on other system.

.. _IDLE: http://hkn.eecs.berkeley.edu/~dyoo/python/idle_intro/


Variables
---------

Basic data types
''''''''''''''''

* Python has strings, integers, floating point numbers, Boolean values
  (``True`` and ``False``) similarly as most other programming languages.

* Strings can be enclosed into double or single quotes (they do not
  have any difference like they do for example in Perl).

* Unicode strings have a special syntax like ``u"Hyv\xE4\xE4 y\xF6\t\xE4!"``
  Using Unicode with Python is not covered otherwise in this tutorial.

* ``None`` is a special value meaning nothing similarly as ``null`` in
  Java.

* Try at least these on the interpreter:

  .. sourcecode:: pycon

    >>> 2 * 2.5
    5.0
    >>> 'This is easy'
    'This is easy'
    >>> "Ain't it"
    "Ain't it"


Declaring variables
'''''''''''''''''''

* All different values can be assigned to variables. Valid characters
  in variable identifiers are letters, underscore, and numbers,
  although numbers cannot start the variable name.

* A variable needs not to be declared, it starts to exist when a value is
  assigned for the first time.

* There is no need to specify the variable type either as the type is
  got from the assigned variable automatically.

* Try it out:

  .. sourcecode:: pycon

    >>> a = 3
    >>> a
    3
    >>> b = 4
    >>> a*b
    12
    >>> greeting = 'Hello'
    >>> greeting
    'Hello'

* It is even possible to assign multiple variables at once:

  .. sourcecode:: pycon

    >>> x, y = 'first', 'second'
    >>> x
    'first'


First program
-------------

* Create a file ``hello.py`` with your editor of choice and write this
  content into it:

  .. sourcecode:: python

    print "Hello, world!"

* Then execute the file on the console like this:

  .. sourcecode:: console

    python hello.py

* As a result you should get ``Hello, world!`` printed into the screen.

* For more interesting examples see `Dive Into Python`__.

__ http://diveintopython.org/getting_to_know_python/index.html


Functions
---------

Creating functions
''''''''''''''''''

* Creating functions in Python is super easy. This example uses the
  interpreter again, but you can also write the code into the prevous
  ``hello.py`` file.

  .. sourcecode:: pycon

     >>> def hello():
     ...     print "Hello, world!"
     ... 
     >>> hello()
     Hello, world!

* Note that in Python code blocks must be indented (four spaces is the
  norm and highly recommended) and you close the block simply by
  returning to the earlier indentation level.

* Note also that this ``hello`` function is actually already a valid
  keyword for Robot Framework!

* A function with arguments is not that more complicated:

  .. sourcecode:: pycon

    >>> def hello(name):
    ...     print "Hello, %s!" % name
    ...
    >>> hello("Python")
    Hello, Python!
    >>> hello("Robot Framework")
    Hello, Robot Framework!

* The hard part in this example is string formatting (i.e. ``"Hello,
  %s!" % name``). Python has similar string formatting as for example C.
  More information about it can be found e.g. from `Dive Into Python`__.

__ http://diveintopython.org/native_data_types/formatting_strings.html


Documenting functions
'''''''''''''''''''''

* In Python functions, as well as classes and modules, are documented with
  so called `doc strings`_:

  .. sourcecode:: pycon

     >>> def hello():
     ...     """Prints 'Hello, world!' to the standard output."""
     ...     print "Hello, world!"
     ... 

* Interestingly the documentation is available dynamically:
 
  .. sourcecode:: pycon
     >>> print hello.__doc__
     Prints 'Hello, world!' to the standard output.

* Robot Framework has `libdoc.py`_ tool that can generate test library
  documentation based on these doc strings. Documenting functions that
  are used as keywords is thus very important.

.. _doc strings: http://diveintopython.org/getting_to_know_python/documenting_functions.html
.. _libdoc.py: http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool


Optional and named arguments
''''''''''''''''''''''''''''

* Functions can have default values for some or all of its arguments:

  .. sourcecode:: pycon

    >>> def hello(name="World"):
    ...     print "Hello, %s!" % name
    ...
    >>> hello()
    Hello, World!
    >>> hello("Robot")
    Hello, Robot!

* If there are several optional arguments, it is also possible to
  specify only some of them by giving their name along with the value
  as the example below illustrates. Those arguments that do not have
  default values cannot be omited.

  .. sourcecode:: pycon

    >>> def test(a, b=1, c=2, d=3):
    ...   print a, b, c, d
    ...
    >>> test(0)
    0 1 2 3
    >>> test(0, 42)
    0 42 2 3
    >>> test(1, c=10)
    1 1 10 3
    >>> test(2, c=100, d=200)
    2 1 100 200

* Robot Framework keywords can have default values but they are always
  used with positional arguments. For example if above ``hello``
  method was used as a keyword, it could be used with zero or one
  argument, and ``test`` could be used with one to four arguments.

* For more information about optional and named arguments, see `Dive Into Python`__.

__ http://diveintopython.org/power_of_introspection/optional_arguments.html


Variable number of arguments
''''''''''''''''''''''''''''

* Function can also be created so that they take any number of
  arguments. This is done by prefixing an argument after required and
  optional arguments with an asterisk like ``*args``, and it means that
  the specified argument gets all the "extra" arguments as a tuple.

  .. sourcecode:: pycon

    >>> def example(arg1, arg2, *rest):
    ...     print arg1, arg2, rest
    ...
    >>> example(1, 2)
    1 2 ()
    >>> example(1, 2, 3)
    1 2 (3,)
    >>> example(1, 2, 3, 4, 5)
    1 2 (3, 4, 5)

* Using variable number of arguments works also with Robot Framework
  keywords.

* `Python tutorial`__ explains everything in this and earlier section in
  detail.

.. __: http://docs.python.org/tut/node6.html#SECTION006700000000000000000


Returning values
''''''''''''''''

* Functions can use ``return`` statement to return values that can be
  assigned to variables or passed to other functions:

  .. sourcecode:: pycon

   >>> def multiply_by_two(number):
   ...     return number * 2
   ... 
   >>> result = multiply_by_two(10)
   >>> result
   20
   >>> result = multiply_by_two(multiply_by_two(2))
   >>> result
   8

* Robot Framework keywords can also return values that can be assigned
  to variables and then used as arguments to other keywords.


Container data types
--------------------

* Python has a nice set of container data types build into the
  language with a really simple syntax similarly as in Perl and
  Ruby. You are going to use them a lot!

* See for example `Dive Into Python`__ for more information and examples
  than shown here.

__ http://diveintopython.org/native_data_types/


Lists
'''''

* A list is an ordered collection of items which you normally access
  by index.

  .. sourcecode:: pycon

    >>> x = ['Some', 'strings', 'here']
    >>> x[0]
    'Some'
    >>> x[1]
    'strings'
    >>> x[-1]
    'here'
    >>> x[2] = x[2].upper()
    >>> x.append(42)
    >>> x
    ['Some', 'strings', 'HERE', 42]

Tuples
''''''

* A tuple is a list like structure which you cannot alter after creating it.

  .. sourcecode:: pycon

    >>> t = (1, 2, 'x')
    >>> t[0]
    1
    >>> t[-1]
    'x'
    >>> t[0] = 'new value'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: 'tuple' object does not support item assignment

Dictionaries
''''''''''''

* A dictionary is an unordered collection of key-value pairs. Called
  hashmap in some other languages.

  .. sourcecode:: pycon

    >>> d = {'x': 'some value', 'a': 1, 'b': 2}
    >>> d['a']
    1
    >>> d['x']
    'some value'
    >>> d['a'] = d['b']
    >>> d['tuple'] = t
    >>> d
    {'a': 2, 'x': 'some value', 'b': 2, 'tuple': (1, 2, 'x')}


Control Flow
------------

Conditional execution
'''''''''''''''''''''

* Python has similar :code:`if/elif/else` structure as most other
  programming languages.

* Notice that no parantheses are needed around the expression as, for
  example, Java and C require.

  .. sourcecode:: python

    def is_positive(number):
    	if number > 0:
            return True
        else:
            return False

    def greet(name, time):
        if 7 < time < 12:
            print 'Good morning %s' % name
        elif time < 18:
            print 'Good afternoon %s' % name
        elif time < 23:
            print 'Good night %s' % name
	else:
            print '%s, you should be sleeping!' % name


Looping
'''''''

* For loop allows iterating over a sequence of items such as
  list. This is probably the loop you are going to use most often.

  .. sourcecode:: python

    def greet_many(names):
        for name in names:
            print 'Hello %s' % name

    def count_up(limit):
        for num in range(limit):
            if num == 0:
                print 'Blastoff!'
            else:
                print num

* While loop iterates as long as given expression is true. Very handy
  in testing when waiting some event to occur.

  .. sourcecode:: python

    def wait_until_message_received:
        msg = try_to_receive_message()
        while msg is None:
            time.sleep(5)
            msg = try_to_receive_message()
        return msg
            
* Both for and while loops have typical :code:`continue` and
  :code:`break` statements that can be used to end the current
  iteration or exit the loop altogether.

* Quite often for loops can be replaced with even more concise list
  comprehensions or generator expressions:

  .. sourcecode:: pycon
  
    >>> numbers = [1, -5, 4, -32, 0, 42]
    >>> positive = [ num for num in numbers if num > 0 ]
    >>> positive
    [1, 4, 42]
    >>> sum(num for num in positive)
    47

* For more examples and information:

  - http://docs.python.org/tut/node6.html
  - http://diveintopython.org/file_handling/for_loops.html
  - http://diveintopython.org/native_data_types/mapping_lists.html


Modules
-------

Importing modules
'''''''''''''''''

* Importing existing Python modules is as simply as saying :code:`import
  modulename`. 

* An alternative syntax is :code:`from modulename import something`. 

* Python has a comprehensive `standard library`_ so there is plenty of
  existing code to be imported. It is recommended to study what is
  available to avoid reinventing wheels.


Creating modules
''''''''''''''''

* Every :path:`.py` file is effectively a Python module, so you have
  already created at least :code:`hello` module.

* For example we could have following code in a file called  :path:`example.py`:

  .. sourcecode:: python

    def hello(name="World"):
        print "Hello, %s!" % name

    if __name__ == "__main__":
        hello()

  and then be able to use it like:

  .. sourcecode:: pycon

    >>> import example
    >>> example.hello("Tellus")
    Hello, Tellus!

* :code:`if __name__ == "__main__"` block in the previous example is
  important because it allows executing the file also as a script like
  :cli:`python example.py`. Automatic :code:`__name__` attribute
  (Python has many of these as you will see if you study it more) gets
  value :code:`"__main___"` when the file is run as a script and the
  if block is thus executed only in that case.

* Bigger modules can be organized into several files inside a higher
  level module as submodules. In this case the higher level module is
  a directory with a special :path:`___init___.py` file.

* For more information about modules see http://docs.python.org/tut/node8.html

.. _standard library: http://docs.python.org/lib/lib.html


Module search path (PYTHONPATH)
'''''''''''''''''''''''''''''''

* Python modules are not automatically searched everywhere on you
  machine. Python has certain default places to search modules for
  (e.g. its own library directory which is often in place like
  :path:`C:\Python26\Lib` or :path:`/usr/lib/python2.6`) and
  additionally it looks for them from so called :var:`PYTHONPATH`.

* :var:`PYTHONPATH` is most often controlled using an environment
  variable with the same name that contains places (mainly
  directories) to look for Python modules. It is similar to Java's
  :var:`CLASSPATH` and also to :var:`PATH` environment variable which
  is used by an operating system to look for executable programs.

* :var:`PYTHONPATH` is important also with Robot Framework because it
  can import test libraries only if the module containing the library
  can be imported.


Classes and instances
---------------------

* Python is an object-oriented language but as we have seen you do not
  need to use classes everywhere like you need to with Java. It is
  totally fine to just have a module with functions if that suites
  your needs but object oriented features are often really handy.

* The syntax for creating classes and then instances from them is
  relatively straightforward:

  .. sourcecode:: pycon

    >>> class MyClass:
    ...     def __init__(self, name):
    ...         self._name = name
    ...     def hello(self, other="World"):
    ...         print "%s says hello to %s." % (self._name, other)
    ... 
    >>> c = MyClass('Robot')
    >>> c.hello()
    Robot says hello to World.
    >>> c.hello('Tellus')
    Robot says hello to Tellus.

* The only surprising part in the syntax is that every class method
  must have :code:`self` as the first argument in the signature. After
  you create an instance of the class Python binds the method and
  takes care of passing the :code:`self` argument automatically so you
  do not use it when calling the method.

* To learn more about classes you can follow `a pretty interesting
  example from Dive Into Python
  <http://diveintopython.org/object_oriented_framework/index.html>`_
  or/and study `a detailed information from Python Tutorial
  <http://docs.python.org/tut/node11.html>`_


Exceptions
----------

* Python has an exception system similar to many other languages.
  Exceptions are classes and the normal way to raise them is
  :code:`raise SomeException("Error message")`.

* Exceptions are handled in a :code:`try/except` block which can have
  an optional :code:`finally` branch.

* Compared to Java there are some terminology differences
  (:code:`raise` vs. :code:`throw` and :code:`except`
  vs. :code:`catch`) but the biggest real difference to is that there
  are no checked exceptions. This means that you do not need to add
  :code:`throws SomeException` to methods that may raise an exception.

* More info: http://diveintopython.org/file_handling/index.html

* Exceptions are an important part of the Robot Framework Library API
  because keywords use them to communicate failures to the framework.


Regular Expressions
-------------------

* Regular expressions are really handy for processing strings which is
  a really common need in test automation.

* Python has a really fast regular expression engine and it uses a
  syntax derived from Perl's regexp syntax similarly as Java and many
  other languages.

* A good introduction is
  http://diveintopython.org/regular_expressions/index.html


Unit Testing
------------

* Unit testing is important especially when you start having more
  code and unit testing your test library code can be a really good
  idea.

* Python has several unit testing frameworks. Two of them,
  :code:`unittest` and :code:`doctest`, are in the standard
  library. The former is immediately familiar for anyone who has used
  JUnit or some other xUnit framework and the other is interesting
  because it allows using function doc strings for tests.

* Dive Into Python has really good chapters about

  - `unit testing`_,
  - `test-driven development`_ (TDD), and
  - refactoring_.

.. _unit testing: http://diveintopython.org/unit_testing/index.html
.. _test-driven development: http://diveintopython.org/unit_testing/stage_1.html
.. _refactoring: http://diveintopython.org/refactoring/index.html


Writing Test Libraries
----------------------

Robot Framework's test library API is really simple. It is explained
fully in the `User Guide`_ but the basic features are covered here
with an example.

The test library can be either a module or a class.  In case of a
module, a keyword will be created for each top-level function in the
module. In case of a class, a keyword will be created for each public
method of the class.

Keyword may return values using the :code:`return` statement, a
failure is generated by raising an exception, and :code:`print`
statement can be used to log a message from a keyword. The example
library below illustrates these features:

.. sourcecode:: python
   
   ./ExampleLibrary.py

These keyword may be tested for example using a TSV test file below:

.. csv-table::
   :class: tsv-example
   :file: example_tests.tsv
   :delim: tab


.. footer:: Generated by reStructuredText_. Syntax highlighting by Pygments_.

.. _user guide: http://code.google.com/p/robotframework/wiki/UserGuide
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Pygments: http://pygments.org/
