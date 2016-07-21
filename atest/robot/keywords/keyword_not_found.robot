*** Settings ***
Documentation     Test for using non-existing keywords.
...
...               Tests for existing keywords and too many matching keywords
...               are in keyword_namespaces.robot.
Suite Setup       Run Tests    ${EMPTY}    keywords/keyword_not_found.robot
Resource          atest_resource.robot

*** Test Cases ***
Non Existing Implicit Keyword
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Non Existing Explicit Keyword
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Non Existing Implicit In User Keyword
    Check Test Case    ${TEST NAME}

Non Existing Explicit In User Keyword
    Check Test Case    ${TEST NAME}

Non Existing Library
    Check Test Case    ${TEST NAME}
