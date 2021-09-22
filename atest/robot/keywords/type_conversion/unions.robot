*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/unions.robot
Resource          atest_resource.robot

*** Test Cases ***
Union
    Check Test Case    ${TESTNAME}

Union with None and without str
    Check Test Case    ${TESTNAME}

Union with None and str
    Check Test Case    ${TESTNAME}

Union with ABC
    Check Test Case    ${TESTNAME}

Union with subscripted generics
    Check Test Case    ${TESTNAME}

Union with subscripted generics and str
    Check Test Case    ${TESTNAME}

Union with TypedDict
    Check Test Case    ${TESTNAME}

Union with item not liking isinstance
    Check Test Case    ${TESTNAME}

Argument not matching union
    Check Test Case    ${TESTNAME}

Union with custom type
    Check Test Case    ${TESTNAME}

Multiple types using tuple
    Check Test Case    ${TESTNAME}

Argument not matching tuple types
    Check Test Case    ${TESTNAME}

Optional argument
    Check Test Case    ${TESTNAME}

Optional argument with default
    Check Test Case    ${TESTNAME}

Optional string with None default
    Check Test Case    ${TESTNAME}

String with None default
    Check Test Case    ${TESTNAME}

Avoid unnecessary conversion
    Check Test Case    ${TESTNAME}

Avoid unnecessary conversion with ABC
    Check Test Case    ${TESTNAME}

Union with invalid types
    Check Test Case    ${TESTNAME}

Tuple with invalid types
    Check Test Case    ${TESTNAME}
