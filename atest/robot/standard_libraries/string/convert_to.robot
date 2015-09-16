*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/convert_to.robot
Resource          atest_resource.robot

*** Test Cases ***
Convert To Lowercases
    Check Test Case    ${TESTNAME}

Convert To Uppercases
    Check Test Case    ${TESTNAME}
