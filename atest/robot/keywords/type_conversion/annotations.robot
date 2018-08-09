*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/annotations.robot
Force Tags       require-py3
Resource         atest_resource.robot

*** Test Cases ***
Integer
    Check Test Case    ${TESTNAME}

Float as integer
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

Invalid boolean is accepted as-is
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

Iterable abc
    Check Test Case    ${TESTNAME}

Invalid iterable abc
    Check Test Case    ${TESTNAME}

Mapping abc
    Check Test Case    ${TESTNAME}

Invalid mapping abc
    Check Test Case    ${TESTNAME}

Set abc
    Check Test Case    ${TESTNAME}

Invalid set abc
    Check Test Case    ${TESTNAME}

Enum
    Check Test Case    ${TESTNAME}

Invalid Enum
    Check Test Case    ${TESTNAME}

Bytes
    Check Test Case    ${TESTNAME}

Invalid bytes
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

String is not converted
    Check Test Case    ${TESTNAME}

Unknown types are not converted
    Check Test Case    ${TESTNAME}

Non-strings are not converted
    Check Test Case    ${TESTNAME}

String None is converted to None object
    Check Test Case    ${TESTNAME}
