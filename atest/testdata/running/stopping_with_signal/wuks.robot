*** Settings ***
Library           OperatingSystem

*** Test Cases ***
Test
    [Documentation]    FAIL Execution terminated by signal
    Create File    ${TESTSIGNALFILE}
    Wait Until Keyword Succeeds    10x    10s    Fail    xxx
    Fail    Should not be executed

Test 2
    [Documentation]    FAIL Test execution stopped due to a fatal error.
    Fail    Should not be executed
