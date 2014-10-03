*** Settings ***
Suite Setup     Run tests  ${EMPTY}  variables/variable_table.robot
Force Tags      pybot  jybot  regression
Resource        atest_resource.robot

*** Test Cases ***
Scalar String
    Check Test Case    ${TEST NAME}

Scalar Non-Strings
    Check Test Case    ${TEST NAME}

Scalar String With Escapes
    Check Test Case    ${TEST NAME}

Empty Scalar String
    Check Test Case    ${TEST NAME}

List With One Item
    Check Test Case    ${TEST NAME}

List With Multiple Items
    Check Test Case    ${TEST NAME}

List With Escapes
    Check Test Case    ${TEST NAME}

List Created From List With Escapes
    Check Test Case    ${TEST NAME}

List With No Items
    Check Test Case    ${TEST NAME}

Variable Names Are Case Insensitive
    Check Test Case    ${TEST NAME}

Variable Names Are Space Insensitive
    Check Test Case    ${TEST NAME}

Variable Names Are Underscore Insensitive
    Check Test Case    ${TEST NAME}

Assign Mark With Scalar Variable
    Check Test Case    ${TEST NAME}

Assign Mark With List Variable
    Check Test Case    ${TEST NAME}

Three dots on the same line should be interpreted as string
    Check Test Case     ${TEST NAME}

Using Scalar List Should Fail
    Check Test Case     ${TEST NAME}
    Creating Variable Should Have Failed    ${ERRORS[0]}    \${SCALAR LIST}
    ...    Creating a scalar variable with a list value in the Variable table
    ...    is no longer possible. Create a list variable '\@{SCALAR LIST}'
    ...    and use it as a scalar variable '\${SCALAR LIST}' instead.

Creating variable using non-existing variable fails
    Check Test Case    ${TEST NAME}
    Creating Variable Should Have Failed    ${ERRORS[4]}    \${NONEX 1}
    ...    Variable '\${NON EXISTING}' not found.
    Creating Variable Should Have Failed    ${ERRORS[5]}    \${NONEX 2A}
    ...    Variable '\${NON EX}' not found.*
    Creating Variable Should Have Failed    ${ERRORS[6]}    \${NONEX 2B}
    ...    Variable '\${NONEX 2A}' not found.*

Using variable created from non-existing variable in imports fails
    Creating Variable Should Have Failed    ${ERRORS[1]}    \${NONEX 3}
    ...    Variable '\${NON EXISTING VARIABLE}' not found.
    Import Should Have Failed    ${ERRORS[2]}    Resource
    ...    Variable '\${NONEX 3}' not found.*
    Import Should Have Failed    ${ERRORS[3]}    Library
    ...    Variable '\${NONEX 3}' not found.*

*** Keywords ***
Creating Variable Should Have Failed
    [Arguments]    ${error}    ${name}    @{message}
    ${path} =    Normalize Path    ${DATADIR}/variables/variable_table.robot
    ${msg} =    Catenate
    ...    Error in file '${path}':
    ...    Setting variable '${name}' failed:
    ...    @{message}
    Check Log Message    ${error}    ${msg}    ERROR    pattern=${TRUE}

Import Should Have Failed
    [Arguments]    ${error}    ${name}    @{message}
    ${path} =    Normalize Path    ${DATADIR}/variables/variable_table.robot
    ${msg} =    Catenate
    ...    Error in file '${path}':
    ...    Replacing variables from setting '${name}' failed:
    ...    @{message}
    Check Log Message    ${error}    ${msg}    ERROR    pattern=${TRUE}
