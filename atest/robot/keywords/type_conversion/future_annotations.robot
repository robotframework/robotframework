*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/future_annotations.robot
Force Tags       require-py3.7
Resource         atest_resource.robot

*** Test Cases ***
Concrete types
    Check Test Case    ${TESTNAME}

ABCs
    Check Test Case    ${TESTNAME}

Typing
    Check Test Case    ${TESTNAME}

Invalid
    Check Test Case    ${TESTNAME}
