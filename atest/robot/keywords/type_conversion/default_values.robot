*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/default_values.robot
Resource         atest_resource.robot

*** Test Cases ***
Integer
    Check Test Case    ${TESTNAME}

Integer as float
    Check Test Case    ${TESTNAME}

Float
    Check Test Case    ${TESTNAME}

Decimal
    Check Test Case    ${TESTNAME}

Boolean
    Check Test Case    ${TESTNAME}

Bytes
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Bytearray
    Check Test Case    ${TESTNAME}

Datetime
    Check Test Case    ${TESTNAME}

Date
    Check Test Case    ${TESTNAME}

Timedelta
    Check Test Case    ${TESTNAME}

Enum
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

List
    Check Test Case    ${TESTNAME}

Tuple
    Check Test Case    ${TESTNAME}

Dictionary
    Check Test Case    ${TESTNAME}

Set
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Frozenset
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Sets are not supported in Python 2
    [Tags]    require-py2
    Check Test Case    ${TESTNAME}

None
    Check Test Case    ${TESTNAME}

Invalid values are passed as-is
    Check Test Case    ${TESTNAME}

Strings are not converted
    Check Test Case    ${TESTNAME}

Unknown types are not converted
    Check Test Case    ${TESTNAME}

String None is converted to None object
    Check Test Case    ${TESTNAME}
