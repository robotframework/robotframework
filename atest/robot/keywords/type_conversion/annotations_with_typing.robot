*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/annotations_with_typing.robot
Resource         atest_resource.robot

*** Test Cases ***
List
    Check Test Case    ${TESTNAME}

List with params
    Check Test Case    ${TESTNAME}

Invalid list
    Check Test Case    ${TESTNAME}

Sequence
    Check Test Case    ${TESTNAME}

Sequence with params
    Check Test Case    ${TESTNAME}

Invalid Sequence
    Check Test Case    ${TESTNAME}

Dict
    Check Test Case    ${TESTNAME}

Dict with params
    Check Test Case    ${TESTNAME}

TypedDict
    Check Test Case    ${TESTNAME}

Invalid dictionary
    Check Test Case    ${TESTNAME}

Mapping
    Check Test Case    ${TESTNAME}

Mapping with params
    Check Test Case    ${TESTNAME}

Invalid mapping
    Check Test Case    ${TESTNAME}

Set
    Check Test Case    ${TESTNAME}

Set with params
    Check Test Case    ${TESTNAME}

Invalid Set
    Check Test Case    ${TESTNAME}

None as default
    Check Test Case    ${TESTNAME}

Forward references
    Check Test Case    ${TESTNAME}

Type hint not liking `isinstance`
    Check Test Case    ${TESTNAME}
