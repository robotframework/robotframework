*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/unionsugar.robot
Force Tags        require-py3.10
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

Union with unrecognized type
    Check Test Case    ${TESTNAME}

Union with only unrecognized types
    Check Test Case    ${TESTNAME}

Avoid unnecessary conversion
    Check Test Case    ${TESTNAME}

Avoid unnecessary conversion with ABC
    Check Test Case    ${TESTNAME}
