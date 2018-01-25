*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_with_maximum_time.robot
Resource          atest_resource.robot

*** Test Cases ***
Run Keyword With Maximum Time Failing On Library Keyword
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time Passing On Library Keyword
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time Failing On User Defined Keyword
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time Passing On User Defined Keyword
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time With Failing On Customizable Timeout Keyword
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time With Passing On Customizable Timeout Keyword
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time Failing in Setup
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time Passing in Setup
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time Failing in Teardown
    Check Test Case    ${TESTNAME}

Run Keyword With Maximum Time Passing in Teardown
    Check Test Case    ${TESTNAME}
