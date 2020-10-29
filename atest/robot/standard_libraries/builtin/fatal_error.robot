*** Settings ***
Resource        atest_resource.robot
Suite Setup     Run Tests    ${EMPTY}    standard_libraries/builtin/fatal_error.robot

*** Test Cases ***
Test is stopped when `Fatal Error` keyword is used
    Check Test Case    ${TESTNAME}

Subsequent tests are not executed after `Fatal Error` keyword has been used
    Check Test Case    ${TESTNAME}

Suite teardown is executed after `Fatal Error` keyword
    Check Log Message    ${SUITE.teardown.msgs[0]}    AssertionError    FAIL
