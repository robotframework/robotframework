*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/recursive_definition.robot
Resource         atest_resource.robot

*** Test Cases ***
Direct recursion
    Check Test Case    ${TESTNAME}
    Recursion error    \${DIRECT}    4

Indirect recursion
    Check Test Case    ${TESTNAME}
    Recursion error    \${VAR 1}    8
    Non-existing error    \${VAR 3}    \${VAR 1}    9    \${VAR 3}    \${VAR 2}
    Non-existing error    \${VAR 2}    \${VAR 3}    10    \${VAR 2}

Case-insensitive recursion
    Check Test Case    ${TESTNAME}
    Recursion error    \${xxx}    11

Recursive list variable
    Check Test Case    ${TESTNAME}
    Recursion error    \@{LIST}    5
    Recursion error    \@{LIST 1}    6
    Non-existing error    \@{LIST 2}    \${LIST 1}    7    \${LIST 2}

Recursion with variables used in imports
    Check Test Case    ${TESTNAME}
    Recursion error    \${IMPORT 1}    0
    Non-existing error    \${IMPORT 2}    \${IMPORT 1}    1    \${IMPORT 2}
    Import error    Resource    \${IMPORT 1}    2
    Import error    Library    \${IMPORT 2}    3

*** Keywords ***
Recursion error
    [Arguments]    ${variable}    ${index}
    Error should be    ${index}
    ...    Setting variable '${variable}' failed:
    ...    Recursive variable definition.

Non-existing error
    [Arguments]    ${variable1}    ${variable2}    ${index}    @{recommendations}
    ${recommendations} =    Run Keyword If    ${recommendations}
    ...    Get recommendations    @{recommendations}
    ...    ELSE
    ...    Set variable    ${EMPTY}
    Error should be    ${index}
    ...    Setting variable '${variable1}' failed:
    ...    Variable '${variable2}' not found.
    ...    ${recommendations}

Import error
    [Arguments]    ${setting}    ${variable}    ${index}
    Error should be    ${index}
    ...    Replacing variables from setting '${setting}' failed:
    ...    Variable '${variable}' not found.

Error should be
    [Arguments]    ${index}    @{parts}
    ${path} =    Normalize Path    ${DATADIR}/variables/recursive_definition.robot
    ${error} =   Catenate    Error in file '${path}':    @{parts}
    Check Log Message    ${ERRORS[${index}]}    ${error}    ERROR

Get recommendations
    [Arguments]    @{recommendations}
    ${recommendations} =    Catenate    SEPARATOR=\n${SPACE*4}
    ...    Did you mean:    @{recommendations}
    [Return]    ${recommendations}
