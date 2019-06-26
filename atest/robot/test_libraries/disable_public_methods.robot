*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/disable_public_methods.robot
Resource          atest_resource.robot

*** Test Cases ***
Public Method Is Not Recognized As Keyword
    Check Test Case  ${TESTNAME}

Decorated Method Is Recognized As Keyword
    Check Test Case  ${TESTNAME}

Private Method Is Not Recognized As Keyword
    Check Test Case  ${TESTNAME}

Private Decorated Method Is Recognized As Keyword
    Check Test Case  ${TESTNAME}
