.. include:: <isonum.txt>
.. include:: ../userguide/src/roles.rst


===============================================================
  Python Tutorial for Robot Framework Test Library Developers
===============================================================

| Copyright |copy| Nokia Solutions and Networks 2008-2014
| Licensed under the `Creative Commons Attribution 3.0 Unported`__ license

__ http://creativecommons.org/licenses/by/3.0/

.. contents:: Table of Contents
   :depth: 2


Introduction
============

* This is self learning material to learn how to program using `Python
  language`_. The target is to learn enough Python to be able to start
  creating test libraries for `Robot Framework`_.

* Earlier programming experience is expected but not absolutely
  necessary.

* The main study material for this training is the excellent *Dive Into
  Python* book which is freely available for on-line reading,
  downloading or printing from http://diveintopython.net.  It is
  targeted for people who already know how to program but do not know
  Python before.

* If you are a novice programmer, it might better to start with `Think
  Python`_ book. It is also available for free and its target audience
  is people without any earlier programming knowledge.

* `Python Tutorial`_, available at http://python.org and included in
  the standard Python installation at least on Windows, is also very
  good. Some of the sections in this training refer to it instead of
  or in addition to Dive Into Python.

* Python coding style guidelines are specified in PEP-8_. Notice that
  the Dive Into Python book uses :code:`camelCaseStyle` instead of the
  recommended :code:`underline_style`.

* Another highly recommended style guide, covering many essential
  Python idioms and techniques, is *Code Like a Pythonista:
  Idiomatic Python* available at
  http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html

* The official Python website at http://python.org is a good place to
  find more documentation and Python related information in
  general.

* If you need information about Jython, the Java implementation of
  Python, you can start from http://jython.org.

* *The Definitive Guide to Jython* covers Jython in detail and is
  useful especially if you are interested about Jython-Java
  integration. It is freely available at http://jythonbook.com.


Getting started
===============

Installation
------------

* Most Linux distributions, OS X, and other UNIX like machines have
  Python installed by default, but on Windows you probably need to
  install it separately. Installers for different platforms can be
  found from http://python.org.

* Robot Framework does not yet support Python 3.x versions and this
  tutorial is also based on Python 2.x. Any 2.x version up from 2.3 is
  sufficient but the latter versions are recommended.

* It is highly recommended that you configure your system so that you
  can run Python from command line simply by typing :cli:`python` and pressing
  enter. 

  - On Windows, and possibly on some other systems, this requires
    adding Python installation directory into :var:`PATH` environment
    variable. For example `Robot Framework User Guide`_ has
    instructions on how to do it in its *Installation* section.


Interactive interpreter
-----------------------

* Open the command prompt and type :cli:`python`. On Windows you can
  also start the interpreter by selecting ``Start > All Programs >
  Python 2.x``.

* Statements and expressions can be written in the interpreter.
  Pressing enter will interpret the line and possible results are
  echoed. Try for example:

  .. sourcecode:: pycon

    >>> 1 + 2
    3

* Use :cli:`Ctrl-D` to exit on UNIX like machines and :cli:`Ctrl-Z`
  and enter on Windows.

  - With Python 2.5 and newer you can exit the interpreter also with
    command :code:`exit()`.

* Dive Into Python has some more examples:
  http://diveintopython.net/installing_python/shell.html


Python editors
--------------

* Most general purpose text editors (Emacs, VIM, UltraEdit, ...) and
  IDEs (Eclipse, Netbeans, ...) can be used to edit Python. There are
  also some editors specially for Python.

* The most important editor features are source highlighting and
  handling indentation. Make sure your editor of choice supports them
  either natively or via Python plugin or mode.

* If you do not know any editor, you can at least get started with
  `IDLE`_.  It is included in the standard Python installation on
  Windows and can be installed also on other systems.


Variables
=========

Basic data types
----------------

* Python has strings, integers, floating point numbers, Boolean values
  (:code:`True` and :code:`False`) similarly as most other programming
  languages.

* Strings can be enclosed into double or single quotes. Different
  quotest do not have any difference like they do for example in Perl.

* Unicode strings have a special syntax like :code:`u"Hyv\\xE4\\xE4
  y\\xF6\\t\\xE4!"`. Using Unicode with Python is not covered otherwise
  in this tutorial.

* :code:`None` is a special value meaning nothing similarly as
  :code:`null` in Java.

* Try at least these on the interpreter:

  .. sourcecode:: pycon

    >>> 2 * 2.5
    5.0
    >>> 'This is easy'
    'This is easy'
    >>> "Ain't it"
    "Ain't it"


Declaring variables
-------------------

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
    >>> greeting.upper()
    'HELLO'

* It is even possible to assign multiple variables at once:

  .. sourcecode:: pycon

    >>> x, y = 'first', 'second'
    >>> x
    'first'
    >>> y
    'second'


First program
=============

* Create a file :path:`hello.py` with your editor of choice and write
  this content into it:

  .. sourcecode:: python

    print "Hello, world!"

* Then execute the file on the console like this:

  .. sourcecode:: console

    python hello.py

* As a result you should get :code:`Hello, world!` printed into the
  screen. With Robot Framework keywords such messages would end up
  into the log file.

* For more interesting examples see Dive Into Python:
  http://diveintopython.net/getting_to_know_python/index.html


Functions
=========

Creating functions
------------------

* Creating functions in Python is super easy. This example uses the
  interpreter, but you can also write the code into the previous
  :path:`hello.py` file and execute it.

  .. sourcecode:: pycon

     >>> def hello():
     ...     print "Hello, world!"
     ... 
     >>> hello()
     Hello, world!

* Note that in Python code blocks must be indented (four spaces is the
  norm and highly recommended) and you close the block simply by
  returning to the earlier indentation level. Inside a block you must
  use the indentation level consistently.

* Notice also that this :code:`hello` function is actually already a
  valid keyword for Robot Framework!

* A function with arguments is not that more complicated:

  .. sourcecode:: pycon

    >>> def hello(name):
    ...     print "Hello, %s!" % name
    ...
    >>> hello("Python")
    Hello, Python!
    >>> hello("Robot Framework")
    Hello, Robot Framework!

* The hard part in this example is string formatting (i.e. :code:`"Hello,
  %s!" % name`) which uses similar syntax as for example C language.
  More information about it can be found e.g. from Dive Into Python:
  http://diveintopython.net/native_data_types/formatting_strings.html


Optional and named arguments
----------------------------

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
  default values cannot be omitted.

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
    >>> test(b=0)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: test() takes at least 1 non-keyword argument (0 given)

* Robot Framework keywords can have default values but they are always
  used with positional arguments. For example, if the above :code:`hello`
  method was used as a keyword, it could be used with zero or one
  argument, and :code:`test` could be used with one to four arguments.

* Dive Into Python explains both optional and named arguments very well:
  http://diveintopython.net/power_of_introspection/optional_arguments.html


Variable number of arguments
----------------------------

* Function can also be created so that they take any number of
  arguments. This is done by prefixing an argument after required and
  optional arguments with an asterisk like :code:`*args`, and it means that
  the specified argument gets all the "extra" arguments as a tuple_.

.. _tuple: tuples_

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

* Python tutorial explains everything in this and the prvious section
  in detail:
  http://docs.python.org/tutorial/controlflow.html#more-on-defining-functions


Returning values
----------------

* Functions can use :code:`return` statement to return values that can be
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


Documenting functions
---------------------

* In Python functions, as well as classes and modules, are documented with
  so called doc strings:

  .. sourcecode:: pycon

     >>> def hello():
     ...     """Prints 'Hello, world!' to the standard output."""
     ...     print "Hello, world!"
     ... 

* Interestingly the documentation is available dynamically:
 
  .. sourcecode:: pycon

     >>> print hello.__doc__
     Prints 'Hello, world!' to the standard output.

* Doc strings are covered pretty well in Dive Into Python:
  http://diveintopython.net/getting_to_know_python/documenting_functions.html

* Robot Framework has `libdoc.py`_ tool that can generate test library
  documentation based on these doc strings. Documenting functions that
  are used as keywords is thus very important.


Container data types
====================

* Python has a nice set of container data types built into the
  language with a really simple syntax similarly as in Perl and
  Ruby. You are going to use them a lot!

* See Dive Into Python for more information and examples than shown
  below: http://diveintopython.net/native_data_types


Lists
-----

* A list is an ordered collection of items which you normally access
  by index.

* They also have handy methods like :code:`append`, :code:`insert` and
  :code:`pop` to access or alter the list.

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
------

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

* Notice that you must use a trailing comma to create a tuple with one
  element:

  .. sourcecode:: pycon

    >>> empty = ()
    >>> one = (1,)
    >>> two = (1, 2)


Dictionaries
------------

* A dictionary is an unordered collection of key-value pairs. The same
  data structure is often called hashmap.

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
    >>> 'x' in d
    True
    >>> 'z' in d
    False


Control Flow
============

Conditional execution
---------------------

* Python has similar :code:`if/elif/else` structure as most other
  programming languages.

* Notice that no parentheses are needed around the expression as in
  Java or C.

  .. sourcecode:: python

    def is_positive(number):
    	if number > 0:
            return True
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
-------

* :code:`for` loops allow iterating over a sequence of items such as
  a list. This is probably the loop you are going to use most often.

  .. sourcecode:: python

    def greet_many(names):
        for name in names:
            print 'Hello %s' % name

    def count_up(limit):
        for num in range(1, limit+1):
            if num == limit:
                print 'bye!'
            else:
                print num

* :code:`while` loops iterate as long as given expression is true. Very handy
  when waiting some event to occur.

  .. sourcecode:: python

    def wait_until_message_received():
        msg = try_to_receive_message()
        while msg is None:
            time.sleep(5)
            msg = try_to_receive_message()
        return msg
            
* Both :code:`for` and :code:`while` loops have typical
  :code:`continue` and :code:`break` statements that can be used to
  end the current iteration or exit the loop altogether.

* For more examples and information see:

  - Python Tutorial: http://docs.python.org/tutorial/controlflow.html
  - Dive Into Python: http://diveintopython.net/file_handling/for_loops.html


List comprehensions
-------------------

* Quite often :code:`for` loops can be replaced with even more concise list
  comprehensions or generator expressions:

  .. sourcecode:: pycon
  
    >>> numbers = [1, -5, 4, -32, 0, 42]
    >>> positive = [ num for num in numbers if num > 0 ]
    >>> positive
    [1, 4, 42]
    >>> sum(num * 2 for num in positive)
    94

* This syntax might look a bit strange at first but you will love it
  very soon. To learn more see, for example, Dive Into Python:
  http://diveintopython.net/native_data_types/mapping_lists.html


Modules
=======

Importing modules
-----------------

* Importing existing Python modules is as simply as saying :code:`import
  modulename`. 

* An alternative syntax is :code:`from modulename import something`. 

* Python has a comprehensive `standard library`_ and a `package
  index`_ with external modules so there is plenty of existing code to
  be imported. It is recommended to study what is available to avoid
  reinventing wheels.


Creating modules
----------------

* Because every :path:`.py` file is effectively a Python module, you
  have already created at least :code:`hello` module.

* For example if we have the following code in a file called
  :path:`example.py`:

  .. sourcecode:: python

    def hello(name="World"):
        print "Hello, %s!" % name

    if __name__ == "__main__":
        hello()

  then we can use it in the interpreter (or from other modules) like:

  .. sourcecode:: pycon

    >>> import example
    >>> example.hello("Tellus")
    Hello, Tellus!

* :code:`if __name__ == "__main__"` block in the previous example is
  important because it allows executing the file also as a script like
  :cli:`python example.py`.

* The automatic :code:`__name__` attribute (Python has many of these
  as you will see if you study it more) gets value :code:`"__main___"`
  when the file is run as a script and the :code:`if` block is thus
  executed only in that case.

* Bigger modules can be organized into several files inside a higher
  level module as submodules. In this case the higher level module is
  a directory with a special :path:`___init___.py` file.

* For more information about modules see Python Tutorial:
  http://docs.python.org/tutorial/modules.html


Module search path (PYTHONPATH)
-------------------------------

* Python modules are not automatically searched everywhere on you
  machine. Python has certain default places to search modules for
  (e.g. its own library directory which is often in place like
  :path:`C:\\Python26\\Lib` or :path:`/usr/lib/python2.6`) and
  additionally it looks for them from so called :var:`PYTHONPATH`.

* :var:`PYTHONPATH` is most often controlled using an environment
  variable with the same name that contains places (mainly
  directories) to look for Python modules. It is similar to Java's
  :var:`CLASSPATH` and also to :var:`PATH` environment variable which
  is used by an operating system to look for executable programs.

* :var:`PYTHONPATH` is important also with Robot Framework because it
  can import test libraries only if the module containing the library
  can be imported.


Advanced features
=================

Classes and instances
---------------------

* Python is an object-oriented language but as we have seen you do not
  need to use classes everywhere like you need to with Java. It is
  totally fine to just have a module with functions if that suites
  your needs, but object oriented features are often really handy.

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
  you create an instance of the class Python binds the method, and it
  also takes care of passing the :code:`self` argument automatically
  so you do not use it when calling the method.

* To learn more about classes you can follow an interesting example
  from Dive Into Python and/or study detailed information from Python
  Tutorial:

  - http://diveintopython.net/object_oriented_framework
  - http://docs.python.org/tutorial/classes.html

Exceptions
----------

* Python has an exception system similar to many other languages.
  Exceptions are classes and the normal way to raise them is
  :code:`raise SomeException("Error message")`.

* Exceptions are handled in a :code:`try/except` block:

  .. sourcecode:: python

    try:
        f = open(path)
    except IOError, err:
        print "Opening file %s for reading failed: %s" % (path, err)
    
* The :code:`try/except` block can have multiple :code:`except`
  branches, an optional :code:`else` to execute if no exception
  occurred, and :code:`finally` to execute both when an exception
  occurred and when it did not.  

* Compared to Java there are some terminology differences
  (:code:`raise` vs. :code:`throw` and :code:`except`
  vs. :code:`catch`) but the biggest real difference is that there are
  no checked exceptions. This means that you do not need to add
  :code:`throws SomeException` to methods that may raise an exception.

* More information can be found, for example, from Dive Into Python:
  http://diveintopython.net/file_handling/index.html

* Exceptions are an important part of the Robot Framework Library API
  because keywords use them to communicate failures to the framework.


Regular expressions
-------------------

* Regular expressions are really handy for processing strings which is
  a really common need in test automation.

* Python has a really fast regular expression engine and it uses a
  syntax derived from Perl's regexp syntax similarly as Java and many
  other languages.

* Dive Into Python contains a good introduction again:
  http://diveintopython.net/regular_expressions/index.html

* Notice that Python strings also have many useful methods
  (e.g. :code:`startswith`, :code:`find`, :code:`isdigit`) so regexps
  are not needed as often as in Perl or Ruby.


Unit testing
============

* Unit testing is important especially when you start having more
  code and unit testing your test library code can be a really good
  idea.

* Python has several unit testing frameworks. Two of them,
  :code:`unittest` and :code:`doctest`, are in the standard
  library. The former is immediately familiar for anyone who has used
  JUnit or some other xUnit framework and the other is interesting
  because it allows using function doc strings for tests.

* Dive Into Python has really good chapters about `unit testing`__,
  `test-driven development`__ (TDD), and refactoring__.

__ http://diveintopython.net/unit_testing/index.html
__ http://diveintopython.net/unit_testing/stage_1.html
__ http://diveintopython.net/refactoring/index.html


Writing test libraries
======================

Robot Framework's test library API is really simple. It is explained
fully in `Robot Framework User Guide`_ and this tutorial only covers
the very basic features with an executable example.

Library API basics
------------------

The test library can be either a module or a class.  In case of a
module, a keyword will be created for each top-level function in the
module. In case of a class, a keyword will be created for each public
method of the class.

The most important ways keywords can interact with the framework have already
been covered in this tutorial:

* Keyword name maps to the function name (case insensitively and
  underscores removed).
* Keywords have same arguments as implementing functions.
* Failures are reported by raising exceptions.
* :code:`print` statement can be used to log messages.
* Values can be returned using the :code:`return` statement.
* Doc strings are used to document keywords.

Executable example
------------------

The example library and associated test data shown below demonstrate
the most important features of the test library API. You can execute
these test cases in your own environment and edit them to test also
other features. A precondition is having Robot Framework installed__,
but then you only need to get `the library`__ and `the data`__, and
run command :cli:`pybot example_tests.tsv`.

__ http://code.google.com/p/robotframework/wiki/Installation
__ ExampleLibrary.py
__ example_tests.tsv

.. sourcecode:: python
   
   ./ExampleLibrary.py

.. csv-table:: Simple test cases using keywords from ExampleLibrary
   :class: tsv-example
   :file: example_tests.tsv
   :delim: tab


.. footer:: Generated by reStructuredText_. Syntax highlighting by Pygments_.

.. _Python language: http://python.org
.. _Robot Framework: http://robotframework.org
.. _Think Python: http://www.greenteapress.com/thinkpython/thinkpython.html
.. _Python Tutorial: http://docs.python.org/tutorial
.. _PEP-8: http://www.python.org/dev/peps/pep-0008/
.. _Robot Framework User Guide: http://code.google.com/p/robotframework/wiki/UserGuide
.. _libdoc.py: http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool
.. _IDLE: http://hkn.eecs.berkeley.edu/~dyoo/python/idle_intro/
.. _standard library: http://docs.python.org/lib/lib.html
.. _package index: http://pypi.python.org
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Pygments: http://pygments.org/
