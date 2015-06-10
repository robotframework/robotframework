*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_if_test_passed_failed
Force Tags        regression
Default Tags      jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
Run Keyword If test Failed When Test Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.teardown.kws[0].name}    BuiltIn.Log
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    Hello from teardown!

Run Keyword If test Failed When Test Does Not Fail
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.teardown.keywords}

Run Keyword If Test Failed Can't Be Used In Setup
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.setup.keywords}

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

Run Keyword If Test Passed When Test Passes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    Teardown of passing test

Run Keyword If Test Passed When Test Fails
    Check Test Case    ${TEST NAME}

Run Keyword If Test Passed Can't Be used In Setup
    Check Test Case    ${TEST NAME}

Run Keyword If Test Passed Can't Be used In Test
    Check Test Case    ${TEST NAME}

Run Keyword If Test Passes Uses User Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.kws[0].kws[0].msgs[0]}    Teardown message
    Check KW Arguments    ${tc.teardown.kws[0].kws[0]}    \${message}

Run Keyword If Test Passed Fails
    Check Test Case    ${TEST NAME}

Run Keyword If Test Passed When Teardown Fails
    Check Test Case    ${TEST NAME}

Run Keyword If Test Failed When Teardown Fails
    Check Test Case    ${TEST NAME}

Continuable Failure In Teardown
    Check Test Case    ${TEST NAME}

Run Keyword If test Passed Can't Be Used In Suite Setup or Teardown
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${SUITE.suites[2].setup.msgs[0]}    Keyword 'Run Keyword If Test Passed' can only be used in test teardown.    FAIL
    Check Log Message    ${SUITE.suites[2].teardown.msgs[0]}    Keyword 'Run Keyword If Test Passed' can only be used in test teardown.    FAIL

Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    Run Keyword If Test Failed Uses User Keyword
    Check KW Arguments    ${tc.teardown}    Teardown UK    \${TEARDOWN MESSAGE}
    Check KW Arguments    ${tc.teardown.kws[0]}    \${TEARDOWN MESSAGE}
    Check KW Arguments    ${tc.teardown.kws[0].kws[0]}    \${message}
