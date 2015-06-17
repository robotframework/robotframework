*** Settings ***
Suite Teardown    My Suite Teardown
Library           Library.py
Library           OperatingSystem

*** Test Case ***
Test
    [Documentation]    FAIL Execution terminated by signal
    Create File    ${TESTSIGNALFILE}
    Busy Sleep    2
    Fail    Should not be executed
    [Teardown]    Log    Logging Test Case Teardown

Test 2
    [Documentation]    FAIL Test execution stopped due to a fatal error.
    Fail    Should not be executed

*** Keywords ***
My Suite Teardown
    Log    Logging Suite Teardown
    Sleep    ${TEARDOWN SLEEP}
