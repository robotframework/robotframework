*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/process/stdin.robot
Resource          atest_resource.robot

*** Test Cases ***
Stdin is PIPE by defauls
    Check Test Case    ${TESTNAME}

Stdin as PIPE explicitly
    Check Test Case    ${TESTNAME}

Stdin can be disabled
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Stdin can be disabled with None object
    Check Test Case    ${TESTNAME}

Stdin as file
    Check Test Case    ${TESTNAME}

Stdin as text
    Check Test Case    ${TESTNAME}

Stdin as stdout from other process
    Check Test Case    ${TESTNAME}
