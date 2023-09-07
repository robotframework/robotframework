..
   When parsing ReST files, only robotframework code blocks
   and includes need to be parsed.
.. include:: empty.rest
.. include:: include.rst

.. Sphinx directive, causes error with plain docutils.
.. highlight:: robotframework


ReST Test Data Example
======================

This text should be ignored, even though it's not a comment.
We have a devious plan to rule the world with robots.

.. code:: robotframework

   *Settings*      *Value*

   Documentation  A complex testdata file in rst format.
   # Default Tags are in include.rst
   Force Tags     force1   force2

   Suite Setup    Log   Setup
   Test Teardown  Log   Test Teardown
   Resource       ../resources/rest_directive_resource.rst
   | Variables  | ../resources/variables.py
   | Library    | OperatingSystem | | | | | | | | | | | | | | | |
   Invalid    Setting

.. csv-table:: cannot and should not be parsed
   :file: not/a/real/path.csv

The following are non-standard docutils directives and no errors
should arise when parsing this.

Testing also a :term:`test` as it should not generate an error.

.. highlight:: robotframework

.. todo::
   This is not really a todo so you have to do nothing.

.. automodule:: some_module
   :members:
   :undoc-members:
   :show-inheritance:

Please ignore me and the non-robotframework code blocks below.

.. code:: python

def ignore_me_or_die():
    raise SystemExit('I did warn you!!')

.. code:: NonExistingProgrammingLanguage

   *** Settings ***
   Documentation    This Robot data in non-robot code block should be ignored.
   Force Tags       do    not    add    us

   *** Test Cases ****
   Ignore me or die
       Fatal Error    I did warn you!!

.. code:: robotframework

          * Variables

          ${table_var}   foo
          @{table_listvar}   bar   ${table_var}
          ${quoted}   """this has """"many "" quotes """""
          ${single_quoted}   s'ingle'qu'ot'es''

We support also `code-block` and `sourcecode` directives as alias for `code`.

.. code-block:: robotframework

   ***Test Cases***

   Passing   Log   Passing test case.

.. sourcecode:: robotframework

   Failing        [Documentation]   FAIL    Failing test case.
      Fail                          Failing test case.
   User Keyword   [DocumentAtion]   FAIL    A cunning argument. != something
      My Keyword With Arg           A cunning argument.

   Nön-äscïï
      [Documentation]   FAIL Nön-äscïï error
      Fail    Nön-äscïï error

   | Own Tags     | [Tags]       | own1      | own2
   |              | Log          | tags test |
   |              |              |
   | Default Tags | No Operation |

   Variable Table
      Should Be Equal   ${table_var}   foo
      Should Be Equal   ${table_listvar}[0]   bar
      Should Be Equal   ${table_listvar}[1]   foo

   Resource File
      Keyword from ReST resource
      Keyword from ReST resource 2
      Should Be Equal   ${rest_resource_var}   ReST Resource Variable
      Should Be Equal   ${rest_resource_var2}   ReST Resource Variable From Recursive Resource

   Variable File
      Should Be Equal   ${file_listvar}[0]   ${True}
      Should Be Equal   ${file_listvar}[1]   ${3.14}
      Should Be Equal   ${file_listvar}[2]   Hello, world!!
      Should Be Equal   ${file_var1}   ${-314}
      Should Be Equal   ${file_var2}   file variable 2

   Library Import   Directory Should Not Be Empty   ${CURDIR}

   Test Timeout   [Timeout]   0.01s
      [Documentation]   FAIL   Test timeout 10 milliseconds exceeded.
      Sleep   2

   Keyword Timeout   [Documentation]   FAIL   Keyword timeout 2 milliseconds exceeded.
      Timeouted Keyword

   Empty Rows
      [Documentation]   Testing that empty rows are ignored.   FAIL Expected failure.

      No operation

      Fail   Expected failure.

   Document   [Documentation]   Testing the metadata parsing.
      no operation

   Default Fixture   No operation

   Overridden Fixture   [Teardown]   Fail   Failing Teardown
      [Setup]   Log   Own Setup
      [Documentation]   FAIL   Teardown failed:\nFailing Teardown
      No Operation

   Quotes   Should Be Equal   ${quoted}   """this has """"many "" quotes """""
      Should Be Equal   ${single_quoted}   s'ingle'qu'ot'es''

   Escaping
      Should Be Equal    -c:\\temp-\t-\x00-\${x}-    ${ESCAPING}

.. code:: robotframework

   *Keywords*   *Action*   *Argument*   *Argument*   *Argument*

   My Keyword With Arg   [Arguments]   ${arg1}
      Keyword with no arguments
      Another Keyword   ${arg1}

   Another Keyword   [Arguments]   ${arg1}   ${arg2}=something
      Should Be Equal   ${arg1}   ${arg2}

   Timeouted Keyword   [Timeout]   2ms
      Sleep   2

   Keyword With No Arguments   Log   Hello world!
