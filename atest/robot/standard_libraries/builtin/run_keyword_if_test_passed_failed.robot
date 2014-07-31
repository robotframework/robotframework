*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_if_test_passed_failed
Force Tags        regression
Default Tags      jybot    pybot
Resource          atest_resource.txt


*** Test Case ***
Run Keyword If test Failed When Test Fails
    ${tc} =    Check Test Case    Run Keyword If test Failed When Test Fails
    Equals    ${tc.teardown.kws[0].name}    BuiltIn.Log
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    Hello from teardown!

Run Keyword If test Failed When Test Does Not Fail
    ${tc} =    Check Test Case    Run Keyword If test Failed When Test Does Not Fail
    Ints Equal    ${tc.teardown.keyword_count}    0

Run Keyword If Test Failed Can't Be Used In Setup
    ${tc} =    Check Test Case    Run Keyword If Test Failed Can't Be Used In Setup
    Ints Equal    ${tc.setup.keyword_count}    0

Run Keyword If Test Failed Can't Be Used in Test
    Check Test Case    Run Keyword If Test Failed Can't Be Used in Test

Run Keyword If Test Failed Uses User Keyword
    ${tc} =    Check Test Case    Run Keyword If Test Failed Uses User Keyword
    Check Log Message    ${tc.teardown.kws[0].kws[0].msgs[0]}    Teardown message

Run Keyword If Test Failed Fails
    Check Test Case    Run Keyword If Test Failed Fails

Run Keyword If test Failed Can't Be Used In Suite Setup or Teardown
    ${tc} =    Check Test Case    Run Keyword If test Failed Can't Be Used In Suite Setup or Teardown
    Check Log Message    ${SUITE.suites[0].setup.msgs[0]}    Keyword 'Run Keyword If Test Failed' can only be used in test teardown    FAIL
    Check Log Message    ${SUITE.suites[0].teardown.msgs[0]}    Keyword 'Run Keyword If Test Failed' can only be used in test teardown    FAIL

Run Keyword If Test Passed When Test Passes
    ${tc} =    Check Test Case    Run Keyword If Test Passed When Test Passes
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    Teardown of passing test

Run Keyword If Test Passed When Test Fails
    Check Test Case    Run Keyword If Test Passed When Test Fails

Run Keyword If Test Passed Can't Be used In Setup
    Check Test Case    Run Keyword If Test Passed Can't Be used In Setup

Run Keyword If Test Passed Can't Be used In Test
    Check Test Case    Run Keyword If Test Passed Can't Be used In Test

Run Keyword If Test Passes Uses User Keyword
    ${tc} =    Check Test Case    Run Keyword If Test Passes Uses User Keyword
    Check Log Message    ${tc.teardown.kws[0].kws[0].msgs[0]}    Teardown message
    Check KW Arguments    ${tc.teardown.kws[0].kws[0]}    \${message}

Run Keyword If Test Passed Fails
    Check Test Case    Run Keyword If Test Passed Fails

Run Keyword If test Passed Can't Be Used In Suite Setup or Teardown
    ${tc} =    Check Test Case    Run Keyword If test Passed Can't Be Used In Suite Setup or Teardown
    Check Log Message    ${SUITE.suites[2].setup.msgs[0]}    Keyword 'Run Keyword If Test Passed' can only be used in test teardown    FAIL
    Check Log Message    ${SUITE.suites[2].teardown.msgs[0]}    Keyword 'Run Keyword If Test Passed' can only be used in test teardown    FAIL

Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    Run Keyword If Test Failed Uses User Keyword
    Check KW Arguments    ${tc.teardown}    Teardown UK    \${TEARDOWN MESSAGE}
    Check KW Arguments    ${tc.teardown.kws[0]}    \${TEARDOWN MESSAGE}
    Check KW Arguments    ${tc.teardown.kws[0].kws[0]}    \${message}
