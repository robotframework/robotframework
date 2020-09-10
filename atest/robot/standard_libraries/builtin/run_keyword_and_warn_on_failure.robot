*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/run_keyword_and_warn_on_failure.robot
Resource        atest_resource.robot

*** Test Cases ***
Run Keyword And Warn On Failure
    Check Test Case  ${TESTNAME}

Run Keyword And Warn On Failure For Keyword Teardown
    Check Test Case  ${TESTNAME}

Run User keyword And Warn On Failure
    Check Test Case  ${TESTNAME}

Run Keyword And Warn On Failure With Syntax Error
    Check Test Case  ${TESTNAME}

Run Keyword And Warn On Failure With Failure On Test Teardown
    Check Test Case  ${TESTNAME}