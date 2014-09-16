***Settings***
Documentation   This suite was initially created for testing keyword types with
...             listeners but can be used for other purposes too.
Suite Setup     ${SUITE SETUP}
Suite Teardown  ${SUITE TEARDOWN}
Test Setup      Test Setup
Test Teardown   Test Teardown

*** Variables ***
${SUITE SETUP}       Suite Setup
${SUITE TEARDOWN}    Suite Teardown

***Test Cases***

Test with setup and teardown
    Keyword

Test with failing setup
    [Setup]    Fail    Test Setup
    Fail    Should not be executed

Test with failing teardown
    Keyword
    [Teardown]    Fail    Test Teardown

Failing test with failing teardown
    Fail    Keyword
    [Teardown]    Fail    Test Teardown

***Keywords***

Suite Setup
    Log  Suite Setup

Suite Teardown
    Log  Suite Teardown

Test Setup
    Log  Test Setup

Test Teardown
    Log  Test Teardown

Keyword
    Log  Keyword
