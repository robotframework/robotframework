*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/embedded_arguments.robot
Resource         atest_resource.robot

*** Test Cases ***
Types via annotations
    Check Test Case    ${TESTNAME}

Types via @keyword
    Check Test Case    ${TESTNAME}

Types via defaults
    Check Test Case    ${TESTNAME}
