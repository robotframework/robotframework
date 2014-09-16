*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/time_calculations.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Time addition to time should succeed
    Check Test Case    ${TESTNAME}

Time subtraction from time should succeed
    Check Test Case    ${TESTNAME}
