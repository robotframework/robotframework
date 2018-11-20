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

Java types
    [Tags]    require-jython
    Check Test Case    ${TESTNAME}
