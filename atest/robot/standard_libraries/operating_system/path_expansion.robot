*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/path_expansion.robot
Resource          atest_resource.robot

*** Test Cases ***
Tilde in path
    Check testcase    ${TESTNAME}

Tilde and username in path
    Check testcase    ${TESTNAME}
