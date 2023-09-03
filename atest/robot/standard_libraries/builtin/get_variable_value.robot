*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/get_variable_value.robot
Resource        atest_resource.robot

*** Test Cases ***
Get value when variable exists
    Check Test Case  ${TESTNAME}

Get value when variable doesn't exist
    Check Test Case  ${TESTNAME}

Get value when default value is none
    Check Test Case  ${TESTNAME}

Default value contains variables
    Check Test Case  ${TESTNAME}

Use escaped variable syntaxes
    Check Test Case  ${TESTNAME}

List variables
    Check Test Case  ${TESTNAME}

Extended variable syntax
    Check Test Case  ${TESTNAME}

Nested variable
    Check Test Case  ${TESTNAME}

List and dict variable items
    Check Test Case  ${TESTNAME}

Invalid variable syntax
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2
    Check Test Case  ${TESTNAME} 3
