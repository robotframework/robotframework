*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/add_time_to_date.robot
Resource         atest_resource.robot

*** Test Cases ***
Time addition to date should succeed
    Check Test Case    ${TESTNAME}

Time addition to date over DST boundary
    Check Test Case    ${TESTNAME}
