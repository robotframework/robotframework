*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/continue_on_failure.robot running/continue_on_failure_in_suite_setup.robot
Resource          atest_resource.robot

*** Test Cases ***

Continue in test
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}    This should be executed

Continue in user keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 1, 0]}    This should be executed in Test Case

Continue in test with several continuable failures
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}    This should be executed
    Check Log Message    ${tc[3, 0]}    This should also be executed
    Check Log Message    ${tc[5, 0]}    This too should also be executed

Continue in user keyword with several continuable failures
    ${tc}=    Check Test Case    ${TESTNAME}
    Verify all failures in user keyword    ${tc[0]}    Test Case
    Verify all failures in user keyword    ${tc[1]}    Test Case, Again

Continuable and regular failure
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.body}          4
    Should Be Equal     ${tc[-1].status}    NOT RUN

Continue in nested user keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 1, 0]}    This should be executed in Top Level UK (with ∏ön ÄßÇïï €§)
    Verify all failures in user keyword    ${tc[0, 2]}    Nested UK

Continuable and regular failure in UK
    Check Test Case    ${TESTNAME}

Several continuable failures and regular failure in nested UK
    ${tc}=    Check Test Case    ${TESTNAME}
    Verify all failures in user keyword    ${tc[0, 2]}    Nested UK
    Verify all failures in user keyword    ${tc[1, 1, 2]}    Nested UK

Continue when setting variables
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    \${ret} = None
    Check Log Message    ${tc[0, 1]}    ContinuableApocalypseException: Can be continued    FAIL
    Check Log Message    ${tc[2, 0]}    \${r1} = None
    Check Log Message    ${tc[2, 1]}    \${r2} = None
    Check Log Message    ${tc[2, 2]}    \${r3} = None
    Check Log Message    ${tc[2, 3]}    ContinuableApocalypseException: Can be continued    FAIL
    Check Log Message    ${tc[4, 0]}    \@{list} = [ ]
    Check Log Message    ${tc[4, 1]}    ContinuableApocalypseException: Can be continued    FAIL
    Check Log Message    ${tc[6, 0]}    No jokes    FAIL
    Length Should Be     ${tc[6].body}     1

Continuable failure in user keyword returning value
    Check Test Case    ${TESTNAME}

Continue in test setup
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.setup[1, 0]}    This should be executed in Test Setup
    Should Be Empty      ${tc.body}

Continue in test teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown[1, 0]}    This should be executed in Test Teardown

Continue many times in test setup and teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Verify all failures in user keyword    ${tc.setup}       Test Setup
    Should Be Empty                        ${tc.body}
    Verify all failures in user keyword    ${tc.teardown}    Test Teardown

Continue in suite teardown
    ${suite}=    Get Test Suite    Continue On Failure
    Check Log Message    ${suite.teardown[1, 0]}    This should be executed in Suite Teardown

Continue in suite setup
    ${suite}=    Get Test Suite    Continue On Failure In Suite Setup
    Check Log Message    ${suite.setup[1, 0]}    This should be executed in Suite Setup (with ∏ön ÄßÇïï €§)

Continue in for loop
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0, 0]}    ContinuableApocalypseException: 0    FAIL
    Check Log Message    ${tc[0, 0, 1, 0]}    This should be executed inside for loop
    Check Log Message    ${tc[0, 1, 0, 0]}    ContinuableApocalypseException: 1    FAIL
    Check Log Message    ${tc[0, 1, 1, 0]}    This should be executed inside for loop
    Check Log Message    ${tc[0, 2, 0, 0]}    ContinuableApocalypseException: 2    FAIL
    Check Log Message    ${tc[0, 2, 1, 0]}    This should be executed inside for loop
    Check Log Message    ${tc[0, 3, 0, 0]}    ContinuableApocalypseException: 3    FAIL
    Check Log Message    ${tc[0, 3, 1, 0]}    This should be executed inside for loop
    Check Log Message    ${tc[0, 4, 0, 0]}    ContinuableApocalypseException: 4    FAIL
    Check Log Message    ${tc[0, 4, 1, 0]}    This should be executed inside for loop
    Check Log Message    ${tc[1, 0]}          This should be executed after for loop

Continuable and regular failure in for loop
    Check Test Case    ${TESTNAME}

robot.api.ContinuableFailure
    Check Test Case    ${TESTNAME}

*** Keywords ***
Verify all failures in user keyword    [Arguments]    ${kw}    ${where}
    Check Log Message    ${kw[0, 0]}    ContinuableApocalypseException: 1    FAIL
    Check Log Message    ${kw[1, 0]}    This should be executed in ${where} (with ∏ön ÄßÇïï €§)
    Check Log Message    ${kw[2, 0]}    ContinuableApocalypseException: 2    FAIL
    Check Log Message    ${kw[3, 0]}    This should also be executed in ${where}
    Check Log Message    ${kw[4, 0]}    ContinuableApocalypseException: 3    FAIL
    Check Log Message    ${kw[5, 0]}    This too should also be executed in ${where}
