*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/wrapping_decorators.robot
Resource          atest_resource.robot

*** Test Cases ***
Wrapped functions
    Check Test Case    ${TESTNAME}

Wrapped function with wrong number of arguments
    Check Test Case    ${TESTNAME}

Wrapped methods
    Check Test Case    ${TESTNAME}

Wrapped method with wrong number of arguments
    Check Test Case    ${TESTNAME}
