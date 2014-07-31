*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/get_variable_value.txt
Force Tags      regression  pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***

Get value when variable exists
    Check Test Case  ${TESTNAME}

Get value when variable doesn't exist
    Check Test Case  ${TESTNAME}

Default value contains variables
    Check Test Case  ${TESTNAME}

Use escaped variable syntaxes
    Check Test Case  ${TESTNAME}

List variables
    Check Test Case  ${TESTNAME}

Invalid variable syntax
    Check Test Case  ${TESTNAME}

