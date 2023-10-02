*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/replace_variables.robot
Resource          atest_resource.robot

*** Test Cases ***
Replace Variables
    Check Test Case    ${TESTNAME}

Replace Variables Using Extended Variable Syntax
    Check Test Case    ${TESTNAME}

Replace Variables Fails When Variable Does Not Exist
    Check Test Case    ${TESTNAME}

Replace Variables With Escaped Variables
    Check Test Case    ${TESTNAME}

Replace Variables With Scalar Object
    Check Test Case    ${TESTNAME}

Replace Variables With List Variable
    Check Test Case    ${TESTNAME}
