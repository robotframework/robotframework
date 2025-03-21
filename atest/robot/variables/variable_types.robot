*** Settings ***
Suite Setup     Run tests    ${EMPTY}    variables/variable_types.robot
Resource        atest_resource.robot

*** Test Cases ***
Variable Section Should Support Types
    Check Test Case    ${TEST NAME}

VAR Should Support Types
    Check Test Case    ${TEST NAME}
