*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/get_current_date.robot
Resource         atest_resource.robot

*** Test Cases ***
Local time
    Check Test Case    ${TESTNAME}

UTC Time
    Check Test Case    ${TESTNAME}

Invalid time zone
    Check Test Case    ${TESTNAME}

Increment
    Check Test Case    ${TESTNAME}

Negative Increment
    Check Test Case    ${TESTNAME}

Default result format
    Check Test Case    ${TESTNAME}

Result format timestamp
    Check Test Case    ${TESTNAME}

Result format custom timestamp
    Check Test Case    ${TESTNAME}

Result format epoch
    Check Test Case    ${TESTNAME}

Local and UTC epoch times are same
    Check Test Case    ${TESTNAME}

Result format datetime
    Check Test Case    ${TESTNAME}
