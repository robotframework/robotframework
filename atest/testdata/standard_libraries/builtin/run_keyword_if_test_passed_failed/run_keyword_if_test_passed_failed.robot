*** Variables ***
${EXPECTED FAILURE}    Expected failure
${TEARDOWN MESSAGE}    Teardown message

*** Test Cases ***
Run Keyword If Test Failed when test fails
    [Documentation]    FAIL Expected failure
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Test Failed    Log    Hello from teardown!

Run Keyword If Test Failed in user keyword when test fails
    [Documentation]    FAIL
    ...    Expected failure
    ...
    ...    Also teardown failed:
    ...    Apparently test failed!
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Test Failed in user keyword

Run Keyword If Test Failed when test passes
    No Operation
    [Teardown]    Run Keyword If Test Failed    Fail    ${NOT EXECUTED}

Run Keyword If Test Failed in user keyword when test passes
    No Operation
    [Teardown]    Run Keyword If Test Failed in user keyword

Run Keyword If Test Failed when test is skipped
    [Documentation]    SKIP For testing purposes.
    Skip    For testing purposes.
    [Teardown]    Run Keyword If Test Failed    Fail    ${NOT EXECUTED}

Run Keyword If Test Failed in user keyword when test is skipped
    [Documentation]    SKIP For testing purposes.
    Skip    For testing purposes.
    [Teardown]    Run Keyword If Test Failed in user keyword

Run Keyword If Test Failed Can't Be Used In Setup
    [Documentation]    FAIL Setup failed:
    ...    Keyword 'Run Keyword If Test Failed' can only be used in test teardown.
    [Setup]    Run Keyword If Test Failed    Fail    ${NOT EXECUTED}
    No Operation

Run Keyword If Test Failed Can't Be Used in Test
    [Documentation]    FAIL Keyword 'Run Keyword If Test Failed' can only be used in test teardown.
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

Run Keyword If Test Passed when test passes
    No Operation
    [Teardown]    Run Keyword If Test Passed    Log    Teardown of passing test

Run Keyword If Test Passed in user keyword when test passes
    [Documentation]    FAIL
    ...    Teardown failed:
    ...    Apparently test passed!
    No Operation
    [Teardown]    Run Keyword If Test Passed in user keyword

Run Keyword If Test Passed when test fails
    [Documentation]    FAIL Expected failure
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Test Passed    Fail    ${NOT EXECUTED}

Run Keyword If Test Passed in user keyword when test fails
    [Documentation]    FAIL Expected failure
    Fail    ${EXPECTED FAILURE}
    [Teardown]    Run Keyword If Test Passed in user keyword

Run Keyword If Test Passed when test is skipped
    [Documentation]    SKIP For testing purposes.
    Skip    For testing purposes.
    [Teardown]    Run Keyword If Test Passed    Fail    ${NOT EXECUTED}

Run Keyword If Test Passed in user keyword when test is skipped
    [Documentation]    SKIP For testing purposes.
    Skip    For testing purposes.
    [Teardown]    Run Keyword If Test Passed in user keyword

Run Keyword If Test Passed Can't Be used In Setup
    [Documentation]    FAIL Setup failed:
    ...    Keyword 'Run Keyword If Test Passed' can only be used in test teardown.
    [Setup]    Run Keyword If Test Passed    Fail    ${NOT EXECUTED}
    No Operation

Run Keyword If Test Passed Can't Be used In Test
    [Documentation]    FAIL Keyword 'Run Keyword If Test Passed' can only be used in test teardown.
    Run Keyword If Test Passed    Fail    ${NOT EXECUTED}

Run Keyword If Test Passes Uses User Keyword
    No Operation
    [Teardown]    Run Keyword If Test Passed    Teardown UK    ${TEARDOWN MESSAGE}

Run Keyword If Test Passed Fails
    [Documentation]    FAIL Teardown failed:
    ...    Expected failure
    No Operation
    [Teardown]    Run Keyword If Test Passed    Fail    ${EXPECTED FAILURE}

Run Keyword If Test Passed When Teardown Fails
    [Documentation]    FAIL Teardown failed:
    ...    Executed
    No Operation
    [Teardown]    Run Keyword If Test Passed When Teardown Fails

Run Keyword If Test Failed When Teardown Fails
    [Documentation]    FAIL Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Deep failure
    ...
    ...    2) Executed
    No Operation
    [Teardown]    Run Keyword If Test Failed When Teardown Fails

Run Keyword If Test Passed/Failed With Earlier Ignored Failures
    No Operation
    [Teardown]    Run Keyword If Test Passed/Failed With Earlier Ignored Failures

Run Keyword If Test Passed/Failed after skip in teardown
    [Documentation]    SKIP For testing purposes
    No Operation
    [Teardown]    Run Keyword If Test Passed/Failed after skip

Continuable Failure In Teardown
    [Documentation]    FAIL Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Continuable
    ...
    ...    2) Executed
    No Operation
    [Teardown]    Continuable Failure In Teardown

*** Keywords ***
Run Keyword If Test Failed in user keyword
    Log    Want to have some keyword before Run Keyword If Test Failed
    Run Keyword If Test Failed    Fail    Apparently test failed!

Run Keyword If Test Passed in user keyword
    Log    Want to have some keyword before Run Keyword If Test Passed
    Run Keyword If Test Passed    Fail    Apparently test passed!

Teardown UK
    [Arguments]    ${message}
    Log    ${message}

Run Keyword If Test Passed When Teardown Fails
    Run Keyword If Test Passed    Fail    Executed
    Run Keyword If Test Passed    Fail    Not executed

Run Keyword If Test Failed When Teardown Fails
    Run Keyword If Test Failed    Fail    Not executed
    Failure deeper
    Run Keyword If Test Failed    Fail    Executed

Failure deeper
    Failure even deeper

Failure even deeper
    Fail    Deep failure

Run Keyword If Test Passed/Failed With Earlier Ignored Failures
    Run Keyword And Ignore Error    Fail    Ignored
    Wait Until Keyword Succeeds    10s    0.1s    Fail Once
    ${error1} =
    ...    Run Keyword If Test Passed
    ...    Run Keyword And Expect Error    *
    ...    Fail    Expected 1
    ${error2} =
    ...    Run Keyword And Expect Error    *
    ...    Run Keyword If Test Passed
    ...    Fail    Expected 2
    Should Be Equal    ${error1} - ${error2}    Expected 1 - Expected 2
    Run Keyword If Test Failed    Fail    Not executed

Fail Once
    Log    ${NOT AVAILABLE ON FIRST ROUND}
    [Teardown]    Set Test Variable    ${NOT AVAILABLE ON FIRST ROUND}    xxx

Run Keyword If Test Passed/Failed after skip
    Skip    For testing purposes
    Run Keyword If Test Passed    Fail    ${SHOULD NOT BE RUN}
    Run Keyword If Test Failed    Fail    ${SHOULD NOT BE RUN}

Continuable Failure In Teardown
    Run Keyword And Continue On Failure    Fail    Continuable
    Run Keyword If Test Passed    Fail    Not executed
    Run Keyword If Test Failed    Fail    Executed
