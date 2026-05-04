*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/deferred_annotations.robot
Test Tags        require-py3.14
Resource         atest_resource.robot

*** Test Cases ***
Deferred evaluation of annotations
    [Documentation]    https://peps.python.org/pep-0649
    Check Test Case    ${TESTNAME}

Type checking annotation
    Check Test Case    ${TESTNAME}

Nonexisting annotation
    Check Test Case    ${TESTNAME}

Type checking annotation with parameterized generic
    Check Test Case    ${TESTNAME}
