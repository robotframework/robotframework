*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/keyword_decorator.robot
Resource         atest_resource.robot

*** Test Cases ***
Integer
    Check Test Case    ${TESTNAME}

Integer as hex
    Check Test Case    ${TESTNAME}

Integer as octal
    Check Test Case    ${TESTNAME}

Integer as binary
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

Invalid boolean string is accepted as-is
    Check Test Case    ${TESTNAME}

Invalid boolean
    Check Test Case    ${TESTNAME}

String
    Check Test Case    ${TESTNAME}

Invalid string
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

Flag
    Check Test Case    ${TESTNAME}

IntEnum
    Check Test Case    ${TESTNAME}

IntFlag
    Check Test Case    ${TESTNAME}

Normalized enum member match
    Check Test Case    ${TESTNAME}

Normalized enum member match with multiple matches
    Check Test Case    ${TESTNAME}

Invalid Enum
    Check Test Case    ${TESTNAME}

Invalid IntEnum
    Check Test Case    ${TESTNAME}

NoneType
    Check Test Case    ${TESTNAME}

Invalid NoneType
    Check Test Case    ${TESTNAME}

None
    Check Test Case    ${TESTNAME}

Invalid None
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

Invalid type spec causes error
    Check Test Case    ${TESTNAME}
    Error In Library    KeywordDecorator
    ...    Adding keyword 'invalid_type_spec' failed:
    ...    Type information must be given as a dictionary or a list, got string.
    ...    index=0

Non-matching argument name causes error
    Check Test Case    ${TESTNAME}
    Error In Library    KeywordDecorator
    ...    Adding keyword 'non_matching_name' failed:
    ...    Type information given to non-existing arguments 'no_match' and 'xxx'.
    ...    index=1

Type can be given to `return` without an error
    [Documentation]    `return` isn't used for anything yet, though.
    Check Test Case    ${TESTNAME}

Value contains variable
    Check Test Case    ${TESTNAME}

Default value is not used if explicit type conversion succeeds
    Check Test Case    ${TESTNAME}

Default value is used if explicit type conversion fails
    Check Test Case    ${TESTNAME}

Explicit conversion failure is used if both conversions fail
    Check Test Case    ${TESTNAME}

Multiple types using Union
    Check Test Case    ${TESTNAME}

Argument not matching Union tupes
    Check Test Case    ${TESTNAME}

Multiple types using tuple
    Check Test Case    ${TESTNAME}

Argument not matching tuple tupes
    Check Test Case    ${TESTNAME}
