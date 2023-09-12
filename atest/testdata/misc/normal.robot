*** Settings ***
Documentation     Normal test cases
Force Tags        f1
Default Tags      d1    d_2
Metadata          Something    My Value

*** Variables ***
${DELAY}          0.001    # Make sure elapsed time > 0

*** Test Cases ***
First One
    [Tags]    t1    t2
    Log    Test 1
    Log    Logging with debug level    DEBUG
    logs on trace

Second One
    [Documentation]    Nothing interesting here
    [Timeout]    1 day
    Log    Test 2
    Delay
    Nested keyword
    Nested keyword 2

*** Keywords ***
logs on trace
    [Timeout]    1 hour
    [Tags]    kw    tags
    Log    Log on ${TEST NAME}    TRACE

Delay
    Sleep    ${DELAY}

Nested keyword
    [Tags]    nested
    Nested keyword 2

Nested keyword 2
    [Tags]    nested 2
    Nested keyword 3

Nested keyword 3
    [Tags]    nested 3
    No operation
    RETURN    Just testing...
    Not executed
