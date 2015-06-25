*** Settings ***
Suite Teardown    Sleep    ${TEARDOWN SLEEP}
Library           Library.py
Library           OperatingSystem

*** Test Case ***
Test
    [Documentation]    FAIL Execution terminated by signal
    Create File    ${TESTSIGNALFILE}
    Run Keyword    Busy Sleep    2
    Fail    Should not be executed

Test 2
    [Documentation]    FAIL Test execution stopped due to a fatal error.
    Fail    Should not be executed
