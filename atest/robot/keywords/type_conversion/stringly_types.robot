*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/stringly_types.robot
Resource          atest_resource.robot

*** Test Cases ***
Parameterized list
    Check Test Case    ${TESTNAME}

Parameterized dict
    Check Test Case    ${TESTNAME}

Parameterized set
    Check Test Case    ${TESTNAME}

Parameterized tuple
    Check Test Case    ${TESTNAME}

Homogenous tuple
    Check Test Case    ${TESTNAME}

Union
    Check Test Case    ${TESTNAME}

Nested
    Check Test Case    ${TESTNAME}
