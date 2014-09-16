*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/get_current_date.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Local time increases
    Check Test Case    ${TESTNAME}

UTC Time
    Check Test Case    ${TESTNAME}

Invalid time zone
    Check Test Case    ${TESTNAME}

Increment
    Check Test Case    ${TESTNAME}

Negative Increment
    Check Test Case    ${TESTNAME}

Result format timestamp
    Check Test Case    ${TESTNAME}

Result format epoch
    Check Test Case    ${TESTNAME}

Result format datetime
    Check Test Case    ${TESTNAME}
