*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/literals.robot
Resource          atest_resource.robot

*** Test Cases ***
Literal
    Check Test Case    ${TESTNAME}

Invalid Literal
    Check Test Case    ${TESTNAME}

External literal
    Check Test Case    ${TESTNAME}

literal string is not an alias
    Check Test Case    ${TESTNAME}

Argument not matching
    Check Test Case    ${TESTNAME}

Nested Literal
    Check Test Case    ${TESTNAME}
