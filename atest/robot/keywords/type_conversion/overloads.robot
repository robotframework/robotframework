*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/overloads.robot
Resource          atest_resource.robot

*** Test Cases ***
Annotated
    Check Test Case    ${TESTNAME}

Unannotated
    Check Test Case    ${TESTNAME}
