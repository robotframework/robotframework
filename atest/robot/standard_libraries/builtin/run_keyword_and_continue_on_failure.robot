*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_and_continue_on_failure.robot
Resource          atest_resource.robot

*** Test Cases ***
Run Keyword And Continue On Failure
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Expected Failure    FAIL
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Expected Failure 2    FAIL
    Check Log Message    ${tc.kws[2].msgs[0]}    This should be executed

Run Keyword And Continue On Failure In For Loop
    Check Test Case    ${TESTNAME}

Run User keyword And Continue On Failure
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    This should be executed

Run Keyword And Continue On Failure With For Loops
    Check Test Case    ${TESTNAME}

Nested Run Keyword And Continue On Failure
    Check Test Case    ${TESTNAME}

Run Keyword And Continue On Failure with failure in keyoword teardown
    Check Test Case    ${TESTNAME}

Run Keyword And Continue On Failure With Syntax Error
    Check Test Case    ${TESTNAME}

Run Keyword And Continue On Failure With Timeout
    Check Test Case    ${TESTNAME}

Run Keyword And Continue On Failure With Nonexisting Variable
    Check Test Case    ${TESTNAME}

Run Keyword And Continue On Failure With Nonexisting Extended Variable
    Check Test Case    ${TESTNAME}

Run Keyword And Continue On Failure With Fatal Error
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} 2
