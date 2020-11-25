.. _Evaluating expressions:

Evaluating expressions
======================

Constructs such as `if expression`_ and `inline Python evaluation`_ and
several BuiltIn_ keywords, accept an expression that is evaluated
in Python.

Evaluation namespace
--------------------

Expressions are evaluated using Python's eval__ function so that all Python
built-in functions like `len()` and `int()` are available. In addition to that,
all unrecognized Python variables are considered to be modules that are
automatically imported. It is possible to use all available Python modules,
including the standard modules and the installed third party modules.

Examples:

.. sourcecode:: robotframework

  *** Variables ***
    ${VAR}    123

  *** Test Cases ***
  Use builtins
    Should Be Equal      ${{len('${VAR}')}}        ${3}
    Should Be Equal      ${{int('${VAR}')}}        ${123}

  Access modules
    Should Be Equal      ${{os.sep}}               ${/}
    Should Be Equal      ${{round(math.pi, 2)}}    ${3.14}
    Should Start With    ${{robot.__version__}}    3.

  *** Keywords ***
  Example
    Should Be True  len('${result}') > 3
    IF  os.sep == '/'
        Non-Windows Keyword
    END
    ${robot version} =  Evaluate  robot.__version__


This syntax is basically the same syntax that the :name:`Evaluate` keyword and
some other keywords in the BuiltIn_ library support. The main difference is
that these keywords always evaluate expressions.

A limitation of the `${{expression}}` syntax is that nested modules like
`rootmod.submod` can only be used if the root module automatically imports
the sub module. That is not always the case and using such modules is not
possible. An example that is relevant in the automation context is the
`selenium` module that is implemented, at least at the time of this writing,
so that just importing `selenium` does not import the `selenium.webdriver` sub
module. A workaround is using the aforementioned :name:`Evaluate` keyword
that accepts modules to be imported and added to the evaluation namespace
as an argument:

.. sourcecode:: robotframework

   *** Test Cases ***
   Does not work due to nested module structure
       Log    ${{selenium.webdriver.ChromeOptions()}}

   Evaluate keyword to the rescue
       ${options} =    Evaluate    selenium.webdriver.ChromeOptions()
       ...    modules=selenium.webdriver
       Log    ${options}

__ http://docs.python.org/library/functions.html#eval

Using variables
---------------

When a variable is used in the expression using the normal `${variable}`
syntax, its value is replaced before the expression is evaluated. This
means that the value used in the expression will be the string
representation of the variable value, not the variable value itself.
This is not a problem with numbers and other objects that have a string
representation that can be evaluated directly. For example, if we have
a return code as an integer in variable `${rc}`, using something like
`${{ ${rc} < 10 }}` is fine.

With other objects the behavior depends on the string representation.
Most importantly, strings must always be quoted, and if they can contain
newlines, they must be triple quoted. Examples in the previous section already
showed using `${{len('${VAR}')}}`, and it needed to be converted to
`${{len('''${VAR}''')}}` if the `${VAR}` variable could contain newlines.
This is not that convenient, but luckily there is another alternative
discussed below.

Examples:

.. sourcecode:: robotframework

  *** Keywords ***
  Example
    Should Be True  ${rc} < 10  Return code greater than 10
    IF  '${status}' == 'PASS'
       Log  Passed
    END
    IF  'FAIL' in '${output}'
       Log  Output contains FAIL
    END

Actual variables values are also available in the evaluation namespace.
They can be accessed using special variable syntax without the curly
braces like `$variable` and they must never be quoted.

Using this syntax, the previous examples in this section could be written like `${{ $rc < 10 }}`
and `${{len($VAR)}}`, and the latter would work also if the `${VAR}` variable
contains newlines.


Examples:

.. sourcecode:: robotframework

  *** Keywords ***
  Example
    Should Be True  $rc < 10  Return code greater than 10
    IF  $status == 'PASS'
        Log  Passed
    END
    IF  'FAIL' in $output
        Log  Output contains FAIL
    END
    Should Be True  len($result) > 1 and $result[1] == 'OK'
    Should Be True  $result is not None

Using the `$variable` syntax slows down expression evaluation a little.
This should not typically matter, but should be taken into account if
complex expressions are evaluated often and there are strict time
constrains. Moving such logic to test libraries is typically a good idea
anyway.

Notice that instead of creating complicated expressions, it is often better
to move the logic into a test library. That eases maintenance and can also
enhance execution speed.
