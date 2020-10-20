*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/annotations.robot
Force Tags       require-py3
Resource         atest_resource.robot

*** Test Cases ***
Integer
    Check Test Case    ${TESTNAME}

Invalid integer
    Check Test Case    ${TESTNAME}

Integral (abc)
    Check Test Case    ${TESTNAME}

Invalid integral (abc)
    Check Test Case    ${TESTNAME}

Float
    Check Test Case    ${TESTNAME}

Invalid float
    Check Test Case    ${TESTNAME}

Real (abc)
    Check Test Case    ${TESTNAME}

Invalid real (abc)
    Check Test Case    ${TESTNAME}

Decimal
    Check Test Case    ${TESTNAME}

Invalid decimal
    Check Test Case    ${TESTNAME}

Boolean
    Check Test Case    ${TESTNAME}

Invalid boolean is accepted as-is
    Check Test Case    ${TESTNAME}

String
    Check Test Case    ${TESTNAME}

Bytes
    Check Test Case    ${TESTNAME}

Invalid bytes
    Check Test Case    ${TESTNAME}

Bytestring
    Check Test Case    ${TESTNAME}

Invalid bytesstring
    Check Test Case    ${TESTNAME}

Bytearray
    Check Test Case    ${TESTNAME}

Invalid bytearray
    Check Test Case    ${TESTNAME}

Datetime
    Check Test Case    ${TESTNAME}

Invalid datetime
    Check Test Case    ${TESTNAME}

Date
    Check Test Case    ${TESTNAME}

Invalid date
    Check Test Case    ${TESTNAME}

Timedelta
    Check Test Case    ${TESTNAME}

Invalid timedelta
    Check Test Case    ${TESTNAME}

Enum
    Check Test Case    ${TESTNAME}

Normalized enum member match
    Check Test Case    ${TESTNAME}

Normalized enum member match with multiple matches
    Check Test Case    ${TESTNAME}

Invalid Enum
    Check Test Case    ${TESTNAME}

NoneType
    Check Test Case    ${TESTNAME}

List
    Check Test Case    ${TESTNAME}

Invalid list
    Check Test Case    ${TESTNAME}

Sequence (abc)
    Check Test Case    ${TESTNAME}

Invalid sequence (abc)
    Check Test Case    ${TESTNAME}

Tuple
    Check Test Case    ${TESTNAME}

Invalid tuple
    Check Test Case    ${TESTNAME}

Dictionary
    Check Test Case    ${TESTNAME}

Invalid dictionary
    Check Test Case    ${TESTNAME}

Mapping (abc)
    Check Test Case    ${TESTNAME}

Invalid mapping (abc)
    Check Test Case    ${TESTNAME}

Set
    Check Test Case    ${TESTNAME}

Invalid set
    Check Test Case    ${TESTNAME}

Set (abc)
    Check Test Case    ${TESTNAME}

Invalid set (abc)
    Check Test Case    ${TESTNAME}

Frozenset
    Check Test Case    ${TESTNAME}

Invalid frozenset
    Check Test Case    ${TESTNAME}

Unknown types are not converted
    Check Test Case    ${TESTNAME}

Non-type values don't cause errors
    Check Test Case    ${TESTNAME}

Positional as named
    Check Test Case    ${TESTNAME}

Invalid positional as named
    Check Test Case    ${TESTNAME}

Varargs
    Check Test Case    ${TESTNAME}

Invalid varargs
    Check Test Case    ${TESTNAME}

Kwargs
    Check Test Case    ${TESTNAME}

Invalid Kwargs
    Check Test Case    ${TESTNAME}

Kwonly
    Check Test Case    ${TESTNAME}

Invalid kwonly
    Check Test Case    ${TESTNAME}

Non-strings are not converted
    Check Test Case    ${TESTNAME}

Return value annotation causes no error
    Check Test Case    ${TESTNAME}

None as default
    Check Test Case    ${TESTNAME}

Forward references
    [Tags]    require-py3.5
    Check Test Case    ${TESTNAME}

@keyword decorator overrides annotations
    Check Test Case    ${TESTNAME}

Type information mismatch caused by decorator
    Check Test Case    ${TESTNAME}

Keyword decorator with wraps
    Check Test Case    ${TESTNAME}

Keyword decorator with wraps mismatched type
    Check Test Case    ${TESTNAME}

Value contains variable
    Check Test Case    ${TESTNAME}
