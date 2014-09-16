*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/convert_date_result_format.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Should convert to timestamp
    Check Test Case    ${TESTNAME}

Timestamp should contain millis rounded to three digits
    Check Test Case    ${TESTNAME}

Should convert to timestamp with format
    Check Test Case    ${TESTNAME}

Should convert to epoch
    Check Test Case    ${TESTNAME}

Should convert to datetime
    Check Test Case    ${TESTNAME}

Should exclude milliseconds
    Check Test Case    ${TESTNAME}

Epoch time is float regardless are millis included or not
    Check Test Case    ${TESTNAME}

Formatted with %f in middle
    Check Test Case    ${TESTNAME}
