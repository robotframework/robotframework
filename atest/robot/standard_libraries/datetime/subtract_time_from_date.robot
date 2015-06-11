*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/subtract_time_from_date.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Time subtraction from date should succeed
    Check Test Case    ${TESTNAME}

Time subtraction over DTS boundary
    Check Test Case    ${TESTNAME}
