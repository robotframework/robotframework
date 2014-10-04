*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/recursive_definition.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Direct recursion
    Check Test Case    ${TESTNAME}
    Recursion error    \${VAR}    3

Indirect recursion
    Check Test Case    ${TESTNAME}
    Recursion error    \${V1}    0
    Non-existing error    \${V3}    \${V1}    1
    Non-existing error    \${V2}    \${V3}    2

Case-insensitive recursion
    Check Test Case    ${TESTNAME}
    Recursion error    \${xxx}    4

Recursive list variable
    Check Test Case    ${TESTNAME}
    Recursion error    \@{LIST}    7
    Recursion error    \@{L1}    5
    Non-existing error    \@{L2}    \@{L1}    6

*** Keywords ***
Recursion error
    [Arguments]    ${variable}    ${index}
    ${path} =    Normalize Path    ${DATADIR}/variables/recursive_definition.robot
    ${message} =    Catenate
    ...    Error in file '${path}':
    ...    Setting variable '${variable}' failed:
    ...    Recursive variable definition.
    Check Log Message    ${ERRORS[${index}]}    ${message}    ERROR

Non-existing error
    [Arguments]    ${variable1}    ${variable2}    ${index}
    ${path} =    Normalize Path    ${DATADIR}/variables/recursive_definition.robot
    ${message} =    Catenate
    ...    Error in file '${path}':
    ...    Setting variable '${variable1}' failed:
    ...    Variable '${variable2}' not found.
    Check Log Message    ${ERRORS[${index}]}    ${message}    ERROR
