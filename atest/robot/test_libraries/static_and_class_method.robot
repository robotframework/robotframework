*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/static_and_class_method.robot
Resource          atest_resource.robot

*** Test Cases ***
Class method
    Check Test Case    ${TESTNAME}

Static method
    Check Test Case    ${TESTNAME}
