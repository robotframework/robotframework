*** Settings ***
Suite Setup       Run tests  ${EMPTY}    variables/variable_section.robot
Resource          atest_resource.robot

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

Named based on another variable
    Check Test Case     ${TEST NAME}

Non-existing variable in name
    Creating Variable Should Have Failed    0    32    \${BASED ON \${BAD}}
    ...    Variable '\${BAD}' not found.

Invalid variable name
    Creating Variable Should Have Failed    1    33    Invalid Name
    ...    Invalid variable name 'Invalid Name'.
    Creating Variable Should Have Failed    2    34    \${}
    ...    Invalid variable name '\${}'.
    Creating Variable Should Have Failed    3    35    \${not
    ...    Invalid variable name '\${not'.
    Creating Variable Should Have Failed    4    36    \${not}[[]ok]
    ...    Invalid variable name '\${not}[[]ok]'.

Scalar catenated from multiple values
    Check Test Case     ${TEST NAME}

Scalar catenated from multiple values with 'SEPARATOR' marker
    Check Test Case     ${TEST NAME}

Scalar catenated from multiple values with 'separator' option
    Check Test Case     ${TEST NAME}

Creating variable using non-existing variable fails
    Check Test Case    ${TEST NAME}
    Creating Variable Should Have Failed    8     37    \${NONEX 1}
    ...    Variable '\${NON EXISTING}' not found.
    Creating Variable Should Have Failed    9     38    \${NONEX 2A}
    ...    Variable '\${NON EX}' not found.*
    Creating Variable Should Have Failed    10    39    \${NONEX 2B}
    ...    Variable '\${NONEX 2A}' not found.*

Using variable created from non-existing variable in imports fails
    Creating Variable Should Have Failed    5    40    \${NONEX 3}
    ...    Variable '\${NON EXISTING VARIABLE}' not found.
    Import Should Have Failed               6    43    Resource
    ...    Variable '\${NONEX 3}' not found.*
    Import Should Have Failed               7    44    Library
    ...    Variable '\${NONEX 3}' not found.*

*** Keywords ***
Creating Variable Should Have Failed
    [Arguments]    ${index}    ${lineno}    ${name}    @{message}
    Error In File    ${index}    variables/variable_section.robot    ${lineno}
    ...    Setting variable '${name}' failed:
    ...    @{message}

Import Should Have Failed
    [Arguments]    ${index}    ${lineno}    ${name}    @{message}
    Error In File    ${index}    variables/variable_section.robot    ${lineno}
    ...    Replacing variables from setting '${name}' failed:
    ...    @{message}
