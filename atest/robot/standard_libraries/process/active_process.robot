*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/active_process.robot
Resource         atest_resource.robot

*** Test Cases ***
Implicit handle
    Check Test Case    ${TESTNAME}

Explicit handle
    Check Test Case    ${TESTNAME}

Alias
    Check Test Case    ${TESTNAME}

Implicit handle, explicit handle, and alias are equivalent
    Check Test Case    ${TESTNAME}

Switching active process
    Check Test Case    ${TESTNAME}

Run Process does not change active process
    Check Test Case    ${TESTNAME}
