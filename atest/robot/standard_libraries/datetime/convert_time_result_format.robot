*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/convert_time_result_format.robot
Resource         atest_resource.robot

*** Test Cases ***
Convert to number
    Check Test Case    ${TESTNAME}

Convert to string
    Check Test Case    ${TESTNAME}

Convert to compact string
    Check Test Case    ${TESTNAME}

Convert to timer
    Check Test Case    ${TESTNAME}

Convert to timedelta
    Check Test Case    ${TESTNAME}

Ignore millis
    Check Test Case    ${TESTNAME}

Number is float regardless are millis included or not
    Check Test Case    ${TESTNAME}

Invalid format
    Check Test Case    ${TESTNAME}
