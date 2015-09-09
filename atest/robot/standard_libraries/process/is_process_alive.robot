*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/is_process_alive.robot
Force Tags       regression
Resource         process_resource.robot

*** Test Cases ***
No Process Should Fail
    Check Test Case    ${TESTNAME}

Test Process Should Be Alive
    Check Test Case    ${TESTNAME}

Test Process Should Be Dead
    Check Test Case    ${TESTNAME}
