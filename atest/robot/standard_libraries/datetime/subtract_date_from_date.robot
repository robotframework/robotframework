*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/subtract_date_from_date.robot
Resource         atest_resource.robot

*** Test Cases ***
Subtraction between two dates should succeed
    Check Test Case    ${TESTNAME}

Date subtraction over DST boundary
    Check Test Case    ${TESTNAME}
