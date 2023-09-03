*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/partial.robot
Resource          atest_resource.robot

*** Test Cases ***
Partial function
    Check Test Case    ${TESTNAME}

Partial function with named arguments
    Check Test Case    ${TESTNAME}

Partial function with argument conversion
    Check Test Case    ${TESTNAME}

Partial function with invalid argument count
    Check Test Case    ${TESTNAME}

Partial method
    Check Test Case    ${TESTNAME}

Partial method with named arguments
    Check Test Case    ${TESTNAME}

Partial method with argument conversion
    Check Test Case    ${TESTNAME}

Partial method with invalid argument count
    Check Test Case    ${TESTNAME}
