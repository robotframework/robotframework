*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/deferred_annotations.robot
Force Tags       require-py3.14
Resource         atest_resource.robot

*** Test Cases ***
Type checking annotation
    Check Test Case    ${TESTNAME}

Type checking annotation with mixed types
    Check Test Case    ${TESTNAME}

Nonexisting annotation
    Check Test Case    ${TESTNAME}
