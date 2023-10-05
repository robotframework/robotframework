*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_if_test_passed_failed
Resource          atest_resource.robot

*** Test Cases ***
Run Keyword If Test Failed when test fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.teardown.body[0].full_name}    BuiltIn.Log
    Check Log Message    ${tc.teardown.body[0].msgs[0]}    Hello from teardown!

Run Keyword If Test Failed in user keyword when test fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.body[1].body[0].msgs[0]}    Apparently test failed!    FAIL

Run Keyword If Test Failed when test passes
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body}

Run Keyword If Test Failed in user keyword when test passes
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body[1].body}

Run Keyword If Test Failed when test is skipped
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body}

Run Keyword If Test Failed in user keyword when test is skipped
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body[1].body}

Run Keyword If Test Failed Can't Be Used In Setup
    ${tc} =    Check Test Case    ${TEST NAME}
    Length Should Be     ${tc.setup.body}       1
    Check Log Message    ${tc.setup.body[0]}    Keyword 'Run Keyword If Test Failed' can only be used in test teardown.    FAIL

Run Keyword If Test Failed Can't Be Used in Test
    Check Test Case    ${TEST NAME}

Run Keyword If Test Failed Uses User Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.kws[0].kws[0].msgs[0]}    Teardown message

Run Keyword If Test Failed Fails
    Check Test Case    ${TEST NAME}

Run Keyword If test Failed Can't Be Used In Suite Setup or Teardown
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${SUITE.suites[0].setup.msgs[0]}    Keyword 'Run Keyword If Test Failed' can only be used in test teardown.    FAIL
    Check Log Message    ${SUITE.suites[0].teardown.msgs[0]}    Keyword 'Run Keyword If Test Failed' can only be used in test teardown.    FAIL

Run Keyword If Test Passed when test passes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.body[0].msgs[0]}    Teardown of passing test

Run Keyword If Test Passed in user keyword when test passes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.body[1].body[0].msgs[0]}    Apparently test passed!    FAIL

Run Keyword If Test Passed when test fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body}

Run Keyword If Test Passed in user keyword when test fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body[1].body}

Run Keyword If Test Passed when test is skipped
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body}

Run Keyword If Test Passed in user keyword when test is skipped
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body[1].body}

Run Keyword If Test Passed Can't Be used In Setup
    Check Test Case    ${TEST NAME}

Run Keyword If Test Passed Can't Be used In Test
    Check Test Case    ${TEST NAME}

Run Keyword If Test Passes Uses User Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.kws[0].kws[0].msgs[0]}    Teardown message
    Check Keyword Data    ${tc.teardown.kws[0].kws[0]}    BuiltIn.Log    args=\${message}

Run Keyword If Test Passed Fails
    Check Test Case    ${TEST NAME}

Run Keyword If Test Passed When Teardown Fails
    Check Test Case    ${TEST NAME}

Run Keyword If Test Failed When Teardown Fails
    Check Test Case    ${TEST NAME}

Run Keyword If Test Passed/Failed With Earlier Ignored Failures
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.teardown.kws[0].kws[0].status}    FAIL
    Should Be Equal    ${tc.teardown.kws[0].status}           PASS
    Should Be Equal    ${tc.teardown.kws[1].kws[0].status}    FAIL
    Should Be Equal    ${tc.teardown.kws[1].status}           PASS
    Should Be Equal    ${tc.teardown.status}                  PASS

Run Keyword If Test Passed/Failed after skip in teardown
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.body[1].body}
    Should Be Empty    ${tc.teardown.body[2].body}

Continuable Failure In Teardown
    Check Test Case    ${TEST NAME}

Run Keyword If test Passed Can't Be Used In Suite Setup or Teardown
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${SUITE.suites[2].setup.msgs[0]}    Keyword 'Run Keyword If Test Passed' can only be used in test teardown.    FAIL
    Check Log Message    ${SUITE.suites[2].teardown.msgs[0]}    Keyword 'Run Keyword If Test Passed' can only be used in test teardown.    FAIL

Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    Run Keyword If Test Failed Uses User Keyword
    Check Keyword Data    ${tc.teardown}    BuiltIn.Run Keyword If Test Failed    args=Teardown UK, \${TEARDOWN MESSAGE}    type=TEARDOWN
    Check Keyword Data    ${tc.teardown.kws[0]}    Teardown UK    args=\${TEARDOWN MESSAGE}
    Check Keyword Data    ${tc.teardown.kws[0].kws[0]}    BuiltIn.Log    args=\${message}
