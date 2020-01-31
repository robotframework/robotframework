*** Settings ***
Suite Setup     Run tests    ${EMPTY}    variables/variable_table_in_resource_file.robot
Resource        atest_resource.robot

*** Variables ***
${PATH}         variables/resource_for_variable_table_in_resource_file.robot

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

Scalar catenated from multile values
    Check Test Case     ${TEST NAME}

Creating variable using non-existing variable fails
    Check Test Case    ${TEST NAME}
    Creating Variable Should Have Failed    3    \${NONEX 1}     26
    ...    Variable '\${NON EXISTING}' not found.
    Creating Variable Should Have Failed    4    \${NONEX 2A}    27
    ...    Variable '\${NON EX}' not found.
    ...    Did you mean:*
    Creating Variable Should Have Failed    5    \${NONEX 2B}    28
    ...    Variable '\${NONEX 2A}' not found.
    ...    Did you mean:*

Using variable created from non-existing variable in imports fails
    Creating Variable Should Have Failed    0    \${NONEX 3}     29
    ...    Variable '\${NON EXISTING VARIABLE}' not found.
    Import Should Have Failed               1    Resource        32
    ...    Variable '\${NONEX 3}' not found.
    ...    Did you mean:*
    Import Should Have Failed               2    Library         33
    ...    Variable '\${NONEX 3}' not found.
    ...    Did you mean:*

*** Keywords ***
Creating Variable Should Have Failed
    [Arguments]    ${index}    ${name}    ${lineno}    @{message}
    Error In File    ${index}    ${PATH}    ${lineno}
    ...    Setting variable '${name}' failed:
    ...    @{message}

Import Should Have Failed
    [Arguments]    ${index}    ${name}    ${lineno}    @{message}
    Error In File    ${index}    ${PATH}    ${lineno}
    ...    Replacing variables from setting '${name}' failed:
    ...    @{message}
