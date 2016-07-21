*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/no_active_process.robot
Resource         atest_resource.robot

*** Test Cases ***
No active process
    Check Test Case    ${TESTNAME}

No active process after run process
    Check Test Case    ${TESTNAME}

Invalid handle
    Check Test Case    ${TESTNAME}
