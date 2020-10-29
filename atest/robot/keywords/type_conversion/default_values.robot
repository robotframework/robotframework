*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/default_values.robot
Resource         atest_resource.robot

*** Test Cases ***
Integer
    Check Test Case    ${TESTNAME}

Integer as float
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
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Invalid bytes
    [Tags]    require-py3
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
    [Tags]    require-enum
    Check Test Case    ${TESTNAME}

Invalid enum
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
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Invalid set
    Check Test Case    ${TESTNAME}

Frozenset
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Invalid frozenset
    Check Test Case    ${TESTNAME}

Sets are not supported in Python 2
    [Tags]    require-py2
    Check Test Case    ${TESTNAME}

Unknown types are not converted
    Check Test Case    ${TESTNAME}

Positional as named
    Check Test Case    ${TESTNAME}

Invalid positional as named
    Check Test Case    ${TESTNAME}

Kwonly
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Invalid kwonly
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

@keyword decorator overrides default values
    Check Test Case    ${TESTNAME}
