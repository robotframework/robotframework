*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/continue_on_failure.robot running/continue_on_failure_in_suite_setup.robot
Resource          atest_resource.robot

*** Test Cases ***

Continue in test
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    This should be executed

Continue in user keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    This should be executed in Test Case

Continue in test with several continuable failures
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    This should be executed
    Check Log Message    ${tc.kws[3].msgs[0]}    This should also be executed
    Check Log Message    ${tc.kws[5].msgs[0]}    This too should also be executed

Continue in user keyword with several continuable failures
    ${tc}=    Check Test Case    ${TESTNAME}
    Verify all failures in user keyword    ${tc.kws[0]}    Test Case
    Verify all failures in user keyword    ${tc.kws[1]}    Test Case, Again

Continuable and regular failure
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.kws}    4
    Should Be Equal    ${tc.kws[-1].status}    NOT RUN

Continue in nested user keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    This should be executed in Top Level UK (with ∏ön ÄßÇïï €§)
    Verify all failures in user keyword    ${tc.kws[0].kws[2]}    Nested UK

Continuable and regular failure in UK
    Check Test Case    ${TESTNAME}

Several continuable failures and regular failure in nested UK
    ${tc}=    Check Test Case    ${TESTNAME}
    Verify all failures in user keyword    ${tc.kws[0].kws[2]}    Nested UK
    Verify all failures in user keyword    ${tc.kws[1].kws[1].kws[2]}    Nested UK

Continue when setting variables
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${ret} = None
    Check Log Message    ${tc.kws[0].msgs[1]}    ContinuableApocalypseException: Can be continued    FAIL
    Check Log Message    ${tc.kws[2].msgs[0]}    \${r1} = None
    Check Log Message    ${tc.kws[2].msgs[1]}    \${r2} = None
    Check Log Message    ${tc.kws[2].msgs[2]}    \${r3} = None
    Check Log Message    ${tc.kws[2].msgs[3]}    ContinuableApocalypseException: Can be continued    FAIL
    Check Log Message    ${tc.kws[4].msgs[0]}    \@{list} = [ ]
    Check Log Message    ${tc.kws[4].msgs[1]}    ContinuableApocalypseException: Can be continued    FAIL
    Check Log Message    ${tc.kws[6].msgs[0]}    No jokes    FAIL
    Length Should Be     ${tc.kws[6].msgs}     1

Continuable failure in user keyword returning value
    Check Test Case    ${TESTNAME}

Continue in test setup
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.setup.kws[1].msgs[0]}    This should be executed in Test Setup
    Should Be Empty    ${tc.kws}

Continue in test teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown.kws[1].msgs[0]}    This should be executed in Test Teardown

Continue many times in test setup and teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Verify all failures in user keyword    ${tc.setup}    Test Setup
    Should Be Empty    ${tc.kws}
    Verify all failures in user keyword    ${tc.teardown}    Test Teardown

Continue in suite teardown
    ${suite}=    Get Test Suite    Continue On Failure
    Check Log Message    ${suite.teardown.kws[1].msgs[0]}    This should be executed in Suite Teardown

Continue in suite setup
    ${suite}=    Get Test Suite    Continue On Failure In Suite Setup
    Check Log Message    ${suite.setup.kws[1].msgs[0]}    This should be executed in Suite Setup (with ∏ön ÄßÇïï €§)

Continue in for loop
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    ContinuableApocalypseException: 0    FAIL
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    This should be executed inside for loop
    Check Log Message    ${tc.kws[0].kws[1].kws[0].msgs[0]}    ContinuableApocalypseException: 1    FAIL
    Check Log Message    ${tc.kws[0].kws[1].kws[1].msgs[0]}    This should be executed inside for loop
    Check Log Message    ${tc.kws[0].kws[2].kws[0].msgs[0]}    ContinuableApocalypseException: 2    FAIL
    Check Log Message    ${tc.kws[0].kws[2].kws[1].msgs[0]}    This should be executed inside for loop
    Check Log Message    ${tc.kws[0].kws[3].kws[0].msgs[0]}    ContinuableApocalypseException: 3    FAIL
    Check Log Message    ${tc.kws[0].kws[3].kws[1].msgs[0]}    This should be executed inside for loop
    Check Log Message    ${tc.kws[0].kws[4].kws[0].msgs[0]}    ContinuableApocalypseException: 4    FAIL
    Check Log Message    ${tc.kws[0].kws[4].kws[1].msgs[0]}    This should be executed inside for loop
    Check Log Message    ${tc.kws[1].msgs[0]}    This should be executed after for loop

Continuable and regular failure in for loop
    Check Test Case    ${TESTNAME}

robot.api.ContinuableFailure
    Check Test Case    ${TESTNAME}

*** Keywords ***
Verify all failures in user keyword    [Arguments]    ${kw}    ${where}
    Check Log Message    ${kw.kws[0].msgs[0]}    ContinuableApocalypseException: 1    FAIL
    Check Log Message    ${kw.kws[1].msgs[0]}    This should be executed in ${where} (with ∏ön ÄßÇïï €§)
    Check Log Message    ${kw.kws[2].msgs[0]}    ContinuableApocalypseException: 2    FAIL
    Check Log Message    ${kw.kws[3].msgs[0]}    This should also be executed in ${where}
    Check Log Message    ${kw.kws[4].msgs[0]}    ContinuableApocalypseException: 3    FAIL
    Check Log Message    ${kw.kws[5].msgs[0]}    This too should also be executed in ${where}
