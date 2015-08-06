*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/path_expansion.robot
Force Tags      regression
Resource        atest_resource.robot

*** Test Cases ***
Tilde in path
    [Tags]  pybot  jybot
    Check testcase  ${TESTNAME}

Tilde and username in path
    [Tags]  pybot
    Check testcase  ${TESTNAME}
