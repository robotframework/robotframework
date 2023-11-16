*** Settings ***
Suite Teardown    Async Sleep    ${TEARDOWN SLEEP}
Library           OperatingSystem
Library           Library.py
Library           AsyncStop.py

*** Test Case ***
Test
    [Documentation]    FAIL Execution terminated by signal
    Create File    ${TESTSIGNALFILE}
    Async Test
    Fail    Should not be executed

Test 2
    [Documentation]    FAIL Test execution stopped due to a fatal error.
    Fail    Should not be executed
