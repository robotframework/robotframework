*** Settings ***
Test Timeout      500 milliseconds    My customized ${DEFAULT END}

*** Variables ***
${DEFAULT END}    default test timeout
${MESSAGE}        message from variable

*** Test Cases ***
Default Test Timeout Message
    [Documentation]    FAIL My customized default test timeout
    Sleep    10

Test Timeout Message
    [Documentation]    FAIL My test timeout message
    [Timeout]    100 milliseconds    My test timeout message
    Sleep    10

Test Timeout Message In Multiple Columns
    [Documentation]    FAIL My test timeout message in multiple columns
    [Timeout]    1 millisecond    My    test     timeout     message
    ...    in
    ...    multiple columns
    Sleep    10

Test Timeout Message With Variables
    [Documentation]    FAIL Test ${MESSAGE}
    [Timeout]    200 milliseconds    Test ${MESSAGE}
    Sleep    10

Keyword Timeout Message
    [Documentation]    FAIL My keyword timeout message
    [Timeout]
    Keyword Timeout Message    0.1
    Keyword Timeout Message    10

Keyword Timeout Message In Multiple Columns
    [Documentation]    FAIL My keyword timeout message in multiple columns
    [Timeout]
    Keyword Timeout Message In Multiple Columns    10

Keyword Timeout Message With Variables
    [Documentation]    FAIL Keyword ${MESSAGE}
    [Timeout]
    Keyword Timeout Message With Variables

*** Keywords ***
Keyword Timeout Message
    [Arguments]    ${secs}
    [Timeout]    1 second    My keyword timeout message
    Sleep    ${secs}

Keyword Timeout Message In Multiple Columns
    [Arguments]    ${secs}
    [Timeout]    111 milliseconds    My    keyword     timeout    message
    ...    in
    ...    multiple columns
    Sleep    ${secs}

Keyword Timeout Message With Variables
    [Timeout]    ${0.1} sec    Keyword ${MESSAGE}
    Sleep    5 sec
