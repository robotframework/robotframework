*** Settings ***
Test Setup        Set Log Level    INFO
Library           UseBuiltIn.py
Resource          UseBuiltInResource.robot

*** Test Cases ***
Keywords Using BuiltIn
    Log Messages And Set Log Level
    ${name} =    Get Test Name
    Should Be Equal    ${name}    ${TESTNAME}
    Set New Variable
    Should Be Equal    ${NEW}    Set by library!
    Variable Should Not Exist    ${SET BY LISTENER}

Named argument syntax
    [Documentation]    PASS    The end!
    VAR    ${existing}    ${42}
    Named argument syntax

Listener Using BuiltIn
    Should Be Equal    ${SET BY LISTENER}    quux

Use 'Run Keyword' with non-string values
    Use Run Keyword with non string values

Use dictionary returned by 'Get Variables' with non-string keys
    [Documentation]    FAIL    TypeError: NormalizedDict only accepts strings as keys, got None.
    Use Get Variables dictionary with non string keys

Use BuiltIn keywords with timeouts
    [Timeout]    1 day
    Log Messages And Set Log Level
    Set New Variable
    Should Be Equal    ${NEW}    Set by library!
    Use Run Keyword with non string values

User keyword used via 'Run Keyword'
    User Keyword via Run Keyword

User keyword used via 'Run Keyword' with timeout and trace level
    [Setup]    Set Log Level    TRACE
    [Timeout]    1 day
    User Keyword via Run Keyword

Recursive 'Run Keyword' usage
    Recursive Run Keyword    10

Recursive 'Run Keyword' usage with timeout
    [Documentation]    FAIL    Test timeout 10 milliseconds exceeded.
    [Timeout]    0.01 s
    [Setup]    NONE
    Recursive Run Keyword    1000

Timeout when running keyword that logs huge message
    [Documentation]    FAIL    Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 s
    Run keyword that logs huge message until timeout

Timeout in parent keyword after running keyword
    [Documentation]    FAIL    Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 s
    Timeout in parent keyword after running keyword
