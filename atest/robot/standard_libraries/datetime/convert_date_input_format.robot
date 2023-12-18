*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/convert_date_input_format.robot
Resource         atest_resource.robot

*** Test Cases ***
String inputs
    Check Test Case    ${TESTNAME}

Formatted strings
    Check Test Case    ${TESTNAME}

Formatted with %f in middle
    Check Test Case    ${TESTNAME}

Epoch
    Check Test Case    ${TESTNAME}

Datetime object
    Check Test Case    ${TESTNAME}

Date object
    Check Test Case    ${TESTNAME}

Pad zeroes to missing values
    Check Test Case    ${TESTNAME}

Rounding milliseconds
    Check Test Case    ${TESTNAME}

Invalid input
    Check Test Case    ${TESTNAME}
