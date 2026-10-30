*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/recursion.robot
Test Tags         require-py3.12
Resource          atest_resource.robot

*** Test Cases ***
Valid recursion
    Check Test Case    ${TESTNAME}

Recursion error
    Check Test Case    ${TESTNAME}
