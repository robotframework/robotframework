*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/dynamic.robot
Resource         atest_resource.robot

*** Test Cases ***
List of types
    Check Test Case    ${TESTNAME}

Dict of types
    Check Test Case    ${TESTNAME}

List of aliases
    Check Test Case    ${TESTNAME}

Dict of aliases
    Check Test Case    ${TESTNAME}

Default values
    Check Test Case    ${TESTNAME}

Kwonly defaults
    Check Test Case    ${TESTNAME}

Default values are not used if `get_keyword_types` returns `None`
    Check Test Case    ${TESTNAME}
