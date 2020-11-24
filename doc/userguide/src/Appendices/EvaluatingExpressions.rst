.. _Evaluating expressions:

Evaluating expressions
======================

Constructs such as if expressions and inline Python evaluation and
several BuiltIn keywords, accept an expression that is evaluated
in Python.

Evaluation namespace
--------------------

Expressions are evaluated using Python's
`eval <https://docs.python.org/library/functions.html#eval>`_ function so
that all Python built-ins like ``len()`` and ``int()`` are available.
In addition to that, all unrecognized variables are considered to be
modules that are automatically imported. It is possible to use all
available Python modules, including the standard modules and the installed
third party modules.

Examples:

.. sourcecode:: robotframework

    Should Be True  len('${result}') > 3
    IF  os.sep == '/'
        Non-Windows Keyword
    END
    ${robot version} =  Evaluate  robot.__version__


Using variables
---------------

When a variable is used in the expressing using the normal ``${variable}``
syntax, its value is replaced before the expression is evaluated. This
means that the value used in the expression will be the string
representation of the variable value, not the variable value itself.
This is not a problem with numbers and other objects that have a string
representation that can be evaluated directly, but with other objects
the behavior depends on the string representation. Most importantly,
strings must always be quoted, and if they can contain newlines, they must
be triple quoted.

Examples:

.. sourcecode:: robotframework

    Should Be True  ${rc} < 10  Return code greater than 10
    IF  '${status}' == 'PASS'
       Log  Passed
    END
    IF  'FAIL' in '${output}'
       Log  Output contains FAIL
    END

Actual variables values are also available in the evaluation namespace.
They can be accessed using special variable syntax without the curly
braces like ``$variable``. These variables should never be quoted.

Examples:

.. sourcecode:: robotframework

    Should Be True  $rc < 10  Return code greater than 10
    IF  $status == 'PASS'
        Log  Passed
    END
    IF  'FAIL' in $output
        Log  Output contains FAIL
    END
    Should Be True  len($result) > 1 and $result[1] == 'OK'
    Should Be True  $result is not None

Using the ``$variable`` syntax slows down expression evaluation a little.
This should not typically matter, but should be taken into account if
complex expressions are evaluated often and there are strict time
constrains.

Notice that instead of creating complicated expressions, it is often better
to move the logic into a test library. That eases maintenance and can also
enhance execution speed.
