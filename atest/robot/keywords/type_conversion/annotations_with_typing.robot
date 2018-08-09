*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/annotations_with_typing.robot
Force Tags       require-py3.5
Resource         atest_resource.robot

*** Test Cases ***
Dict
    Check Test Case    ${TESTNAME}

Dict with params
    Check Test Case    ${TESTNAME}

Invalid dictionary
    Check Test Case    ${TESTNAME}

List
    Check Test Case    ${TESTNAME}

List with params
    Check Test Case    ${TESTNAME}

Invalid list
    Check Test Case    ${TESTNAME}

Set
    Check Test Case    ${TESTNAME}

Set with params
    Check Test Case    ${TESTNAME}

Invalid Set
    Check Test Case    ${TESTNAME}

Iterable
    Check Test Case    ${TESTNAME}

Iterable with params
    Check Test Case    ${TESTNAME}

Invalid iterable
    Check Test Case    ${TESTNAME}

Mapping
    Check Test Case    ${TESTNAME}

Mapping with params
    Check Test Case    ${TESTNAME}

Invalid mapping
    Check Test Case    ${TESTNAME}
