*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/get_library_instance.robot
Resource        atest_resource.robot

*** Test Cases ***

Library imported normally
    Check Test Case  ${TESTNAME}

Module library
    Check Test Case  ${TESTNAME}

Java library
    [Tags]  require-jython
    Check Test Case  ${TESTNAME}

Library with alias
    Check Test Case  ${TESTNAME}

`Import Library` keyword
    Check Test Case  ${TESTNAME}

Non-existing library should cause catchable error
    Check Test Case  ${TESTNAME}

Library scopes
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2

