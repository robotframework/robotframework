*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  parsing/data_formats/txt_special_cases
Resource        atest_resource.robot

*** Test Cases ***
Escaping Pipe
    Check Test Case  ${TEST NAME}

Using " In Data
    Check Test Case  ${TEST NAME}

Minimum Spaces
    Check Test Case  ${TEST NAME}

Spaces All Around
    Check Test Case  ${TEST NAME}

Extra Spaces At The End
    Check Test Case  ${TEST NAME}

Using FOR Loop With Spaces
    Check Test Case  ${TEST NAME}

Minimum Pipes
    Check Test Case  ${TEST NAME}

Pipes All Around
    Check Test Case  ${TEST NAME}

Empty line with pipe
    Should Be True    not any(e.level == 'ERROR' for e in $ERRORS)
    Check Test Case  ${TEST NAME}

Pipes In Data
    Check Test Case  ${TEST NAME}

Extra Pipes At The End
    Check Test Case  ${TEST NAME}

Empty Cells In Middle
    Check Test Case  ${TEST NAME}

Consequtive spaces
    Check Test Case  ${TEST NAME}
    Collapsing deprecated    0    foo${SPACE * 12}bar    63
    Collapsing deprecated    1    non-ascii\\xa0\\u1680\\u3000spaces    64

Tabs
    Check Test Case  ${TEST NAME}
    Normalization deprecated    2    foo\\tbar    67
    Collapsing deprecated       3    foo\\t\\t\\tbar    68

Using FOR Loop With Pipes
    Check Test Case  ${TEST NAME}

Tabs In Txt File
    ${tc} =  Check Test Case  Test With Tabs
    Check Log Message  ${tc.kws[0].msgs[0]}  I ignore tabs  DEBUG

*** Keywords ***
Collapsing deprecated
    [Arguments]    ${index}    ${text}    ${line}
    ${path} =    Normalize Path    ${DATADIR}/parsing/data_formats/txt_special_cases/pipes.robot
    ${msg} =    Catenate
    ...    Collapsing consecutive whitespace during parsing is deprecated.
    ...    Fix '${text}' in file '${path}' on line ${line}.
    Check Log Message    ${ERRORS}[${index}]    ${msg}    WARN

Normalization deprecated
    [Arguments]    ${index}    ${text}    ${line}
    ${path} =    Normalize Path    ${DATADIR}/parsing/data_formats/txt_special_cases/pipes.robot
    ${msg} =    Catenate
    ...    Converting whitespace characters to ASCII spaces during parsing is deprecated.
    ...    Fix '${text}' in file '${path}' on line ${line}.
    Check Log Message    ${ERRORS}[${index}]    ${msg}    WARN
