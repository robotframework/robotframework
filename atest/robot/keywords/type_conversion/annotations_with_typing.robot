*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/annotations_with_typing.robot
Resource          atest_resource.robot

*** Test Cases ***
List
    Check Test Case    ${TESTNAME}

List with types
    Check Test Case    ${TESTNAME}

List with incompatible types
    Check Test Case    ${TESTNAME}

Invalid list
    Check Test Case    ${TESTNAME}

Tuple
    Check Test Case    ${TESTNAME}

Tuple with types
    Check Test Case    ${TESTNAME}

Tuple with homogenous types
    Check Test Case    ${TESTNAME}

Tuple with incompatible types
    Check Test Case    ${TESTNAME}

Tuple with wrong number of values
    Check Test Case    ${TESTNAME}

Invalid tuple
    Check Test Case    ${TESTNAME}

Sequence
    Check Test Case    ${TESTNAME}

Sequence with types
    Check Test Case    ${TESTNAME}

Sequence with incompatible types
    Check Test Case    ${TESTNAME}

Invalid sequence
    Check Test Case    ${TESTNAME}

Dict
    Check Test Case    ${TESTNAME}

Dict with types
    Check Test Case    ${TESTNAME}

Dict with incompatible types
    Check Test Case    ${TESTNAME}

Invalid dictionary
    Check Test Case    ${TESTNAME}

Mapping
    Check Test Case    ${TESTNAME}

Mapping with types
    Check Test Case    ${TESTNAME}

Mapping with incompatible types
    Check Test Case    ${TESTNAME}

Invalid mapping
    Check Test Case    ${TESTNAME}

TypedDict
    Check Test Case    ${TESTNAME}

Stringified TypedDict types
    Check Test Case    ${TESTNAME}

Optional TypedDict keys can be omitted (total=False)
    Check Test Case    ${TESTNAME}

Not required TypedDict keys can be omitted (NotRequired/Required)
    Check Test Case    ${TESTNAME}

Required TypedDict keys cannot be omitted
    Check Test Case    ${TESTNAME}

Incompatible TypedDict
    Check Test Case    ${TESTNAME}

Invalid TypedDict
    Check Test Case    ${TESTNAME}

Set
    Check Test Case    ${TESTNAME}

Set with types
    Check Test Case    ${TESTNAME}

Set with incompatible types
    Check Test Case    ${TESTNAME}

Invalid Set
    Check Test Case    ${TESTNAME}

Any
    Check Test Case    ${TESTNAME}

None as default
    Check Test Case    ${TESTNAME}

None as default with Any
    Check Test Case    ${TESTNAME}

Forward references
    Check Test Case    ${TESTNAME}

Type hint not liking `isinstance`
    Check Test Case    ${TESTNAME}
