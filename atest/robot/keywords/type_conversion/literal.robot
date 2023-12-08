*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/literal.robot
Resource          atest_resource.robot

*** Test Cases ***
Integers
    Check Test Case    ${TESTNAME}

Invalid integers
    Check Test Case    ${TESTNAME}

Strings
    Check Test Case    ${TESTNAME}

Strings are case, space, etc. insensitive
    Check Test Case    ${TESTNAME}

Invalid strings
    Check Test Case    ${TESTNAME}

Bytes
    Check Test Case    ${TESTNAME}

Invalid bytes
    Check Test Case    ${TESTNAME}

Booleans
    Check Test Case    ${TESTNAME}

Booleans are localized
    Check Test Case    ${TESTNAME}

Invalid booleans
    Check Test Case    ${TESTNAME}

None
    Check Test Case    ${TESTNAME}

Invalid None
    Check Test Case    ${TESTNAME}

Enums
    Check Test Case    ${TESTNAME}

Invalid enums
    Check Test Case    ${TESTNAME}

Int enums
    Check Test Case    ${TESTNAME}

Invalid int enums
    Check Test Case    ${TESTNAME}

Multiple matches with exact match
    Check Test Case    ${TESTNAME}

Multiple matches with not exact match
    Check Test Case    ${TESTNAME}

In parameters
    Check Test Case    ${TESTNAME}
