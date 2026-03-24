.. _Dynamic library:

Dynamic library API
===================

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
for example, implement each keyword as a separate class.

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
---------------------

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
----------------

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
-------------------------

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
all objects like `('integer', 1)` or `('boolean', True)`. When using other
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
------------------------------

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
--------------------

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

Getting documentation
---------------------

Getting keyword documentation
̃~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If dynamic libraries want to provide keyword documentation, they can implement
the `get_keyword_documentation` method (alias `getKeywordDocumentation`). It
takes a keyword name as an argument and, as the method name implies, returns
its documentation as a string.

The returned documentation is used similarly as the keyword
documentation string with static libraries.
The main use case is getting keywords' documentations into a
library documentation generated by Libdoc_. Additionally,
the first line of the documentation (until the first `\n`) is
shown in log files.

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

Getting source information
--------------------------

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
the imported library class the same way as with the static library API. The
library source path is used with all keywords that do not have their own
source path defined.

.. note:: Returning source information for keywords is a new feature in
          Robot Framework 3.2.

Named argument syntax with dynamic libraries
--------------------------------------------

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
-------------------------------------------

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
-------------------------------------------

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
-------

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
