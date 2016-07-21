*** Settings ***
Documentation     This suite was initially created for testing keyword types
...               with listeners but can be used for other purposes too.
Suite Setup       ${SUITE SETUP}
Suite Teardown    ${SUITE TEARDOWN}
Test Setup        ${TEST SETUP}
Test Teardown     ${TEST TEARDOWN}

*** Variables ***
${SUITE SETUP}       Suite Setup
${SUITE TEARDOWN}    Suite Teardown
${TEST SETUP}        Test Setup
${TEST TEARDOWN}     Test Teardown

*** Test Cases ***
Test with setup and teardown
    Keyword

Test with failing setup
    [Documentation]    FAIL
    ...    Setup failed:
    ...    Test Setup
    [Setup]    Fail    Test Setup
    Fail    Should not be executed

Test with failing teardown
    [Documentation]    FAIL
    ...    Teardown failed:
    ...    Test Teardown
    Keyword
    [Teardown]    Fail    Test Teardown

Failing test with failing teardown
    [Documentation]    FAIL
    ...    Keyword
    ...
    ...    Also teardown failed:
    ...    Test Teardown
    Fail    Keyword
    [Teardown]    Fail    Test Teardown

*** Keywords ***
Suite Setup
    Log    Keyword
    Keyword

Suite Teardown
    Log    Keyword
    Keyword

Test Setup
    Log    Keyword
    Keyword

Test Teardown
    Log    Keyword
    Keyword

Keyword
    Log    Keyword
    [Teardown]    Log    Keyword Teardown
