This text should be ignored, even though it's no a comment.
We have a devious plan to rule the world with robots.

*Settings*      *Value*

Documentation  A complex testdata file in robot format.
Default Tags   default1
Force Tags     force1   force2

Suite Setup    Log   Setup
Test Teardown  Log   Test Teardown
Resource       ../resources/robot_resource.robot
Variables      ../resources/variables.py
Library       OperatingSystem

# This is a normal comment.
 # These
  # are
   # comments
    # as
     # well

* Variables    # comment

${table_var}   foo
@{table_listvar}   bar   ${table_var}
${quoted}   """this has """"many "" quotes """""
${single_quoted}   s'ingle'qu'ot'es''


***Test Cases***

Passing   Log   Passing test case.

Failing        [Documentation]   FAIL    Failing test case.
   Fail                     Failing test case.
User Keyword   [Documentation]   FAIL    A cunning argument. != something
   My Keyword With Arg      A cunning argument.
Nön-äscïï
      [Documentation]   FAIL Nön-äscïï error
      Fail    Nön-äscïï error
Own Tags   [Tags]   own1   own2
   Log   tags test

Default Tags   No Operation

Variable Table   Should Be Equal   ${table_var}   foo
   Should Be Equal   ${table_listvar}[0]   bar
   Should Be Equal   ${table_listvar}[1]   foo


Resource File   Keyword from ROBOT resource
   Keyword from ROBOT resource 2
   Should Be Equal   ${robot_resource_var}   ROBOT Resource Variable
   Should Be Equal   ${robot_resource_var2}   ROBOT Resource Variable From Recursive Resource

Variable File   Should Be Equal   ${file_listvar}[0]   ${True}
   Should Be Equal   ${file_listvar}[1]   ${3.14}
   Should Be Equal   ${file_listvar}[2]   Hello, world!!
   Should Be Equal   ${file_var1}   ${-314}
   Should Be Equal   ${file_var2}   file variable 2


Library Import   Directory Should Not Be Empty   ${CURDIR}





Test Timeout   [Timeout]   0.01second
   [Documentation]   FAIL   Test timeout 10 milliseconds exceeded.
   Sleep   1

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


*Keywords*   *Action*   *Argument*   *Argument*   *Argument*
# comment
My Keyword With Arg   [Arguments]   ${arg1}
# comment
   Keyword with no arguments
   Another Keyword   ${arg1}


 # comment
Another Keyword   [Arguments]   ${arg1}   ${arg2}=something
 # comment
   Should Be Equal   ${arg1}   ${arg2}

Timeouted Keyword   [Timeout]   2ms
   Sleep   0.1

Keyword With No Arguments   Log   Hello world!
