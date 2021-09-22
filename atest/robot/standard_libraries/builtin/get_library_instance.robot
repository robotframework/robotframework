*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/get_library_instance.robot
Resource          atest_resource.robot

*** Test Cases ***
Library imported normally
    Check Test Case    ${TESTNAME}

Module library
    Check Test Case    ${TESTNAME}

Library with alias
    Check Test Case    ${TESTNAME}

Non-exact name
    Check Test Case    ${TESTNAME}

Same name when normalized matching exactly
    Check Test Case    ${TESTNAME}

Same name when normalized matching multiple
    Check Test Case    ${TESTNAME}

`Import Library` keyword
    Check Test Case    ${TESTNAME}

Non-existing library should cause catchable error
    Check Test Case    ${TESTNAME}

Library scopes
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Get all libraries
    Check Test Case    ${TESTNAME}

Get all libraries gets a copy
    Check Test Case    ${TESTNAME}
