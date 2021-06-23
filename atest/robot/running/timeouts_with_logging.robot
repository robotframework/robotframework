*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/timeouts_with_logging.robot
Resource          atest_resource.robot

*** Test Cases ***
Test timeout when logging using RF logger
    Check Test Case    ${TESTNAME}

Keyword timeout when logging using RF logger
    Check Test Case    ${TESTNAME}

Test timeout when logging using Python logger
    Check Test Case    ${TESTNAME}

Keyword timeout when logging using Python logger
    Check Test Case    ${TESTNAME}
