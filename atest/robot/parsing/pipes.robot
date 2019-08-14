*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    parsing/pipes.robot
Resource          atest_resource.robot

*** Test Cases ***
Minimum Pipes
    Check Test Case    ${TEST NAME}

Pipes All Around
    Check Test Case    ${TEST NAME}

Empty line with pipe
    Should Be True    not any(e.level == 'ERROR' for e in $ERRORS)
    Check Test Case    ${TEST NAME}

Pipes In Data
    Check Test Case    ${TEST NAME}

Extra Pipes At The End
    Check Test Case    ${TEST NAME}

Empty Cells In Middle
    Check Test Case    ${TEST NAME}

Consequtive spaces
    Check Test Case  ${TEST NAME}
    Collapsing deprecated       0    foo${SPACE * 12}bar    63
    Collapsing deprecated       1    non-ascii\\xa0\\u1680\\u3000spaces    64

Tabs
    Check Test Case  ${TEST NAME}
    Normalization deprecated    2    foo\\tbar    67
    Collapsing deprecated       3    foo\\t\\t\\tbar    68

Using FOR Loop With Pipes
    Check Test Case  ${TEST NAME}

*** Keywords ***
Collapsing deprecated
    [Arguments]    ${index}    ${text}    ${line}
    ${path} =    Normalize Path    ${DATADIR}/parsing/pipes.robot
    ${msg} =    Catenate
    ...    Collapsing consecutive whitespace during parsing is deprecated.
    ...    Fix '${text}' in file '${path}' on line ${line}.
    Check Log Message    ${ERRORS}[${index}]    ${msg}    WARN

Normalization deprecated
    [Arguments]    ${index}    ${text}    ${line}
    ${path} =    Normalize Path    ${DATADIR}/parsing/pipes.robot
    ${msg} =    Catenate
    ...    Converting whitespace characters to ASCII spaces during parsing is deprecated.
    ...    Fix '${text}' in file '${path}' on line ${line}.
    Check Log Message    ${ERRORS}[${index}]    ${msg}    WARN
