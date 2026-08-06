*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/datetime/convert_date_result_format.robot
Resource          atest_resource.robot

*** Test Cases ***
Timestamp
    Check Test Case    ${TESTNAME}

Milliseconds handling with timestamps
    Check Test Case    ${TESTNAME}

Custom timestamp
    Check Test Case    ${TESTNAME}

Datetime
    Check Test Case    ${TESTNAME}

Date
    Check Test Case    ${TESTNAME}

Epoch
    Check Test Case    ${TESTNAME}

Excluding milliseconds
    Check Test Case    ${TESTNAME}

Epoch is float regardless are millis included or not
    Check Test Case    ${TESTNAME}
