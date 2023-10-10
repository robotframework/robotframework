*** Test Cases ***
Passing setup
    Passing setup

Failing setup
    [Documentation]    FAIL    Hello, setup!
    Failing setup

Failing setup and passing teardown
    [Documentation]    FAIL    Setup failed:\nHello, setup!
    [Setup]    Failing setup and passing teardown
    No Operation

Failing setup and teardown
    [Documentation]    FAIL    Hello, setup!
    ...
    ...    Also keyword teardown failed:
    ...    Hello, teardown!
    Failing setup and teardown

Continue-on-failure mode is not enabled in setup
    [Documentation]    FAIL    Setup failed:\nHello again, setup!
    [Setup]    Continue-on-failure mode is not enabled in setup
    No Operation

NONE is same as no setup
    NONE is same as no setup

Empty [Setup] is same as no setup
    Empty [Setup] is same as no setup

Using variable
    [Documentation]    FAIL    Hello, setup!
    Using variable    Log
    Using variable    None
    Using variable    ${None}
    Using variable    Fail

*** Keywords ***
Passing setup
    [Setup]    Log    Hello, setup!
    Log    Hello, body!

Failing setup
    [Setup]    Fail    Hello, setup!
    Fail    Not executed

Failing setup and passing teardown
    [Setup]    Fail    Hello, setup!
    Fail    Not executed
    [Teardown]    Log    Hello, teardown!

Failing setup and teardown
    [Setup]    Fail    Hello, setup!
    Fail    Not executed
    [Teardown]    Fail    Hello, teardown!

Continue-on-failure mode is not enabled in setup
    [Setup]    Multiple failures
    Fail    Not executed

Multiple failures
    Log     Hello, setup!
    Fail    Hello again, setup!
    Fail    Not executed

NONE is same as no setup
    [Setup]    NONE
    No Operation

Empty [Setup] is same as no setup
    [Setup]
    No Operation

Using variable
    [Arguments]    ${setup}
    [Setup]    ${setup}    Hello, setup!
    No Operation
