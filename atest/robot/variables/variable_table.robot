*** Settings ***
Suite Setup     Run tests  ${EMPTY}  variables/variable_table.robot
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

Invalid variable name
    Parsing Variable Should Have Failed    0    16    Invalid Name
    Parsing Variable Should Have Failed    1    17    \${}
    Parsing Variable Should Have Failed    2    18    \${not
    Parsing Variable Should Have Failed    3    19    \${not}[[]ok]
    Parsing Variable Should Have Failed    4    20    \${not \${ok}}

Scalar catenated from multile values
    Check Test Case     ${TEST NAME}

Creating variable using non-existing variable fails
    Check Test Case    ${TEST NAME}
    Creating Variable Should Have Failed    8     \${NONEX 1}     33
    ...    Variable '\${NON EXISTING}' not found.
    Creating Variable Should Have Failed    9     \${NONEX 2A}    34
    ...    Variable '\${NON EX}' not found.*
    Creating Variable Should Have Failed    10    \${NONEX 2B}    35
    ...    Variable '\${NONEX 2A}' not found.*

Using variable created from non-existing variable in imports fails
    Creating Variable Should Have Failed    5    \${NONEX 3}     36
    ...    Variable '\${NON EXISTING VARIABLE}' not found.
    Import Should Have Failed               6    Resource        39
    ...    Variable '\${NONEX 3}' not found.*
    Import Should Have Failed               7    Library         40
    ...    Variable '\${NONEX 3}' not found.*

*** Keywords ***
Parsing Variable Should Have Failed
    [Arguments]    ${index}    ${lineno}    ${name}
    Error In File    ${index}    variables/variable_table.robot    ${lineno}
    ...    Setting variable '${name}' failed:
    ...    Invalid variable name '${name}'.

Creating Variable Should Have Failed
    [Arguments]    ${index}    ${name}    ${lineno}    @{message}
    Error In File    ${index}    variables/variable_table.robot    ${lineno}
    ...    Setting variable '${name}' failed:
    ...    @{message}

Import Should Have Failed
    [Arguments]    ${index}    ${name}    ${lineno}    @{message}
    Error In File    ${index}    variables/variable_table.robot    ${lineno}
    ...    Replacing variables from setting '${name}' failed:
    ...    @{message}
