*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/keyword_decorator_with_aliases.robot
Resource         atest_resource.robot

*** Test Cases ***
Integer
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
