*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_if_timeout_occurred.robot
Resource          atest_resource.robot

*** Test Cases ***
Run Keyword If Timeout Occurred When Test Timeout Occurred
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred When Test Timeout Did Not Occur
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred When Test Timeout Occurred In Setup
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred When Test Timeout Did Not Occur In Setup
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred When Keyword Timeout Occurred
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred When Keyword Timeout Did Not Occur
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred When Keyword Timeout Occurred In Setup
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred When Keyword Timeout Did Not Occur In Setup
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred Used Outside Teardown
    Check Test Case    ${TESTNAME}

Run Keyword If Timeout Occurred Used When No Timeout Is Set
    Check Test Case    ${TESTNAME}

Returning Value From Run Keyword If Timeout Occurred
    Check Test Case    ${TESTNAME}
