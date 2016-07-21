*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/convert_time_input_format.robot
Resource         atest_resource.robot

*** Test Cases ***
Time string
    Check Test Case    ${TESTNAME}

Number as string
    Check Test Case    ${TESTNAME}

Number
    Check Test Case    ${TESTNAME}

Timer
    Check Test Case    ${TESTNAME}

Timer without millis
    Check Test Case    ${TESTNAME}

Timer without hours
    Check Test Case    ${TESTNAME}

Timedelta
    Check Test Case    ${TESTNAME}

Invalid
    Check Test Case    ${TESTNAME}
