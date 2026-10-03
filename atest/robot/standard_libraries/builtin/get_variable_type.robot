*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/get_variable_type.robot
Resource          atest_resource.robot

*** Test Cases ***
String
    Check Test Case    ${TESTNAME}

Integer
    Check Test Case    ${TESTNAME}

Float
    Check Test Case    ${TESTNAME}

Boolean
    Check Test Case    ${TESTNAME}

List
    Check Test Case    ${TESTNAME}

Dictionary
    Check Test Case    ${TESTNAME}

Tuple
    Check Test Case    ${TESTNAME}

Set
    Check Test Case    ${TESTNAME}

None
    Check Test Case    ${TESTNAME}

Custom object
    Check Test Case    ${TESTNAME}