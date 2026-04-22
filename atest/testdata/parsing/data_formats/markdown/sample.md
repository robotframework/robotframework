Markdown Test Data Example
==========================

This text should be ignored.

```robotframework
*** Settings ***
Documentation    A complex testdata file in md format.
Force Tags       force1    force2
Default Tags     default1
Suite Setup      Log    Setup
Test Teardown    Log    Test Teardown
Resource         ../resources/markdown_resource.md
Variables        ../resources/variables.py
Library          OperatingSystem
Invalid          Setting
```

This non-robot block should be ignored:

```python
def ignore_me():
    raise SystemExit()
```

```robot
*** Variables ***
${table_var}          foo
@{table_listvar}      bar    ${table_var}
${quoted}             """this has """"many "" quotes """""
${single_quoted}      s'ingle'qu'ot'es''
```

``````    robotframework
*** Test Cases ***
Passing    Log    Passing test case.

Failing        [Documentation]    FAIL    Failing test case.
               Fail               Failing test case.

User Keyword   [Documentation]    FAIL    A cunning argument. != something
               My Keyword With Arg    A cunning argument.

Nön-äscïï
               [Documentation]    FAIL Nön-äscïï error
               Fail    Nön-äscïï error

Own Tags       [Tags]    own1    own2
               Log    tags test

Default Tags   No Operation

Variable Table
               Should Be Equal    ${table_var}    foo
               Should Be Equal    ${table_listvar}[0]    bar
               Should Be Equal    ${table_listvar}[1]    foo

Resource File
               Keyword from Markdown resource
               Should Be Equal    ${markdown_resource_var}    Markdown Resource Variable

Variable File
               Should Be Equal    ${file_listvar}[0]    ${True}
               Should Be Equal    ${file_listvar}[1]    ${3.14}
               Should Be Equal    ${file_listvar}[2]    Hello, world!!
               Should Be Equal    ${file_var1}    ${-314}
               Should Be Equal    ${file_var2}    file variable 2

Library Import    Directory Should Not Be Empty    ${CURDIR}

Test Timeout      [Timeout]    0.01s
                  [Documentation]    FAIL    Test timeout 10 milliseconds exceeded.
                  Sleep    2

Keyword Timeout   [Documentation]    FAIL    Keyword timeout 2 milliseconds exceeded.
                  Timeouted Keyword

Empty Rows
               [Documentation]    Testing that empty rows are ignored.    FAIL Expected failure.

               No operation

               Fail    Expected failure.

Document       [Documentation]    Testing the metadata parsing.
               No operation

Default Fixture    No operation

Overridden Fixture    [Teardown]    Fail    Failing Teardown
                      [Setup]      Log     Own Setup
                      [Documentation]    FAIL    Teardown failed:\nFailing Teardown
                      No Operation

Quotes    Should Be Equal    ${quoted}    """this has """"many "" quotes """""
          Should Be Equal    ${single_quoted}    s'ingle'qu'ot'es''

Escaping
          Should Be Equal    -c:\\temp-\t-\x00-\${x}-    ${ESCAPING}
``````````````````````````````````````````````````````````````````

~~~robot works with tildes too and this extra stuff is ignored
*** Keywords ***
My Keyword With Arg    [Arguments]    ${arg1}
                       Keyword with no arguments
                       Another Keyword    ${arg1}

Another Keyword    [Arguments]    ${arg1}    ${arg2}=something
                   Should Be Equal    ${arg1}    ${arg2}

Timeouted Keyword    [Timeout]    2ms
                     Sleep    2

Keyword With No Arguments    Log    Hello world!
~~~
