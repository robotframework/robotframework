*** Variable ***
${EXPECTED FAILURE}    Expected failure
${TEARDOWN MESSAGE}    Teardown message

*** Test Case ***
Run Keyword If test Failed When Test Fails
    [Documentation]    FAIL Expected failure
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Test Failed    Log    Hello from teardown!

Run Keyword If test Failed When Test Does Not Fail
    No Operation
    [Teardown]    Run Keyword If Test Failed    Fail    ${NOT EXECUTED}

Run Keyword If Test Failed Can't Be Used In Setup
    [Documentation]    FAIL Setup failed:
    ...    Keyword 'Run Keyword If Test Failed' can only be used in test teardown
    [Setup]    Run Keyword If Test Failed    Fail    ${NOT EXECUTED}
    No Operation

Run Keyword If Test Failed Can't Be Used in Test
    [Documentation]    FAIL Keyword 'Run Keyword If Test Failed' can only be used in test teardown
    Run Keyword If Test Failed    Fail    ${NOT EXECUTED}

Run Keyword If Test Failed Uses User Keyword
    [Documentation]    FAIL Expected failure
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Test Failed    Teardown UK    ${TEARDOWN MESSAGE}

Run Keyword If Test Failed Fails
    [Documentation]    FAIL Expected failure
    ...
    ...    Also teardown failed:
    ...    Expected teardown failure
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Test Failed    Fail    Expected teardown failure

Run Keyword If Test Passed When Test Passes
    No Operation
    [Teardown]    Run Keyword If Test Passed    Log    Teardown of passing test

Run Keyword If Test Passed When Test Fails
    [Documentation]    FAIL Expected failure
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Test Passed    Fail    This should not be executed

Run Keyword If Test Passed Can't Be used In Setup
    [Documentation]    FAIL Setup failed:
    ...    Keyword 'Run Keyword If Test Passed' can only be used in test teardown
    [Setup]    Run Keyword If Test Passed    Fail    ${NOT EXECUTED}
    No Operation

Run Keyword If Test Passed Can't Be used In Test
    [Documentation]    FAIL Keyword 'Run Keyword If Test Passed' can only be used in test teardown
    Run Keyword If Test Passed    Fail    ${NOT EXECUTED}

Run Keyword If Test Passes Uses User Keyword
    No Operation
    [Teardown]    Run Keyword If Test Passed    Teardown UK    ${TEARDOWN MESSAGE}

Run Keyword If Test Passed Fails
    [Documentation]    FAIL Teardown failed:
    ...    Expected failure
    No Operation
    [Teardown]    Run Keyword If Test Passed    Fail    ${EXPECTED FAILURE}

*** Keyword ***
Teardown UK
    [Arguments]    ${message}
    Log    ${message}
