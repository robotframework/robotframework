*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/default_values.robot
Resource         atest_resource.robot

*** Test Cases ***
Integer
    Check Test Case    ${TESTNAME}

Integer as float
    Check Test Case    ${TESTNAME}

Integer as hex
    Check Test Case    ${TESTNAME}

Integer as octal
    Check Test Case    ${TESTNAME}

Integer as binary
    Check Test Case    ${TESTNAME}

Invalid integer
    Check Test Case    ${TESTNAME}

Float
    Check Test Case    ${TESTNAME}

Invalid float
    Check Test Case    ${TESTNAME}

Decimal
    Check Test Case    ${TESTNAME}

Invalid decimal
    Check Test Case    ${TESTNAME}

Boolean
    Check Test Case    ${TESTNAME}

Invalid boolean
    Check Test Case    ${TESTNAME}

String
    Check Test Case    ${TESTNAME}

Bytes
    Check Test Case    ${TESTNAME}

Invalid bytes
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

Path
    Check Test Case    ${TESTNAME}

Invalid Path
    Check Test Case    ${TESTNAME}

Enum
    Check Test Case    ${TESTNAME}

Flag
    Check Test Case    ${TESTNAME}

IntEnum
    Check Test Case    ${TESTNAME}

IntFlag
    Check Test Case    ${TESTNAME}

Invalid enum
    [Tags]    require-enum
    Check Test Case    ${TESTNAME}

None
    Check Test Case    ${TESTNAME}

List
    Check Test Case    ${TESTNAME}

Invalid list
    Check Test Case    ${TESTNAME}

Tuple
    Check Test Case    ${TESTNAME}

Invalid tuple
    Check Test Case    ${TESTNAME}

Dictionary
    Check Test Case    ${TESTNAME}

Invalid dictionary
    Check Test Case    ${TESTNAME}

Set
    Check Test Case    ${TESTNAME}

Invalid set
    Check Test Case    ${TESTNAME}

Frozenset
    Check Test Case    ${TESTNAME}

Invalid frozenset
    Check Test Case    ${TESTNAME}

Unknown types are not converted
    Check Test Case    ${TESTNAME}

Positional as named
    Check Test Case    ${TESTNAME}

Kwonly
    Check Test Case    ${TESTNAME}

Invalid kwonly
    Check Test Case    ${TESTNAME}

@keyword decorator overrides default values
    Check Test Case    ${TESTNAME}
