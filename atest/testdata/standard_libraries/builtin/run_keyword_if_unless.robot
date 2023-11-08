*** Variables ***
${EXECUTED}             This is executed
@{ARGS WITH ELSE}       ELSE    ${EXECUTED}
@{ARGS WITH ELSE IF}    ELSE IF    ${EXECUTED}
${CATENATE}             Catenate
${FAIL}                 Fail
@{CATENATE STUFF}       Catenate    1    2    \${escaped}    c:\\temp
@{EXPR AND CATENATE}    True    Catenate    \${foo}    ELSE IF    zig    ELSE    bar


*** Test Cases ***
Run Keyword If With True Expression
    Run Keyword If    ${True}    Log    ${EXECUTED}

Run Keyword If With False Expression
    Run Keyword If    0 == 1    Log    ${NON EXISTING}

Run Keyword In User Keyword
    Conditional User Keyword    PASS    ${EXECUTED}
    Conditional User Keyword    FAIL    ${EXECUTED}

Run Keyword With ELSE
    Run Keyword If    ${True}    No Operation    ELSE    Fail
    Run Keyword If    ${True}    Log    ${EXECUTED}    ELSE    Fail    message
    Run Keyword If    ${True}    Log Many    1    2    3    4    ELSE    Fail
    Run Keyword If    ${False}    Non Existing    ${ne1}    ${ne2}    ${ne3}
    ...    ELSE    Log    ${EXECUTED}

Keyword Name in ELSE as variable
    ${ret} =    Run Keyword If    ${1}    ${CATENATE}    1    2    ELSE    ${FAIL}
    Should Be Equal    ${ret}    1 2
    ${ret} =    Run Keyword If    ${0}    ${FAIL}    ELSE    ${CATENATE}    a    b
    Should Be Equal    ${ret}    a b

Keyword Name in ELSE as list variable
    ${ret} =    Run Keyword If    ${0}    ${FAIL}    ELSE    @{CATENATE STUFF}
    Should Be Equal    ${ret}    1 2 \${escaped} c:\\temp
    ${ret} =    Run Keyword If    ${0}    ${FAIL}    ELSE    @{EMPTY}    @{CATENATE STUFF}    foo
    Should Be Equal    ${ret}    1 2 \${escaped} c:\\temp foo

Keyword Name in ELSE as non-existing variable 1
    [Documentation]    FAIL Variable '\${NON EXISTING}' not found.
    Run Keyword If    ${1}    ${NON EXISTING}    ELSE    ${FAIL}

Keyword Name in ELSE as non-existing variable 2
    [Documentation]    FAIL Variable '\${NON EXISTING}' not found.
    Run Keyword If    ${0}    ${FAIL}    ELSE    ${NON EXISTING}

ELSE without keyword is invalid 1
    [Documentation]    FAIL ELSE requires keyword.
    Run Keyword If    ${True}    Catenate    a1    a2    ELSE

ELSE without keyword is invalid 2
    [Documentation]    FAIL ELSE requires keyword.
    Run Keyword If    ${False}    Catenate    a1    a2    ELSE

Only first ELSE is significant
    ${ret} =    Run Keyword If    ${False}    Fail
    ...    ELSE    Catenate    ${EXECUTED}    ELSE    Fail
    Should Be Equal    ${ret}    ${EXECUTED} ELSE Fail

Run Keyword With ELSE IF
    Run Keyword If    ${True}     Log     ${EXECUTED}
    ...    ELSE IF    ${True}     Fail    Should not go here
    Run Keyword If    ${False}    Fail
    ...    ELSE IF    ${True}     Log    ${EXECUTED}

Run Keyword with ELSE IF and ELSE
    Run Keyword If    ${False}    Fail
    ...    ELSE IF    ${True}     Log    ${EXECUTED}
    ...    ELSE       Fail
    Run Keyword If    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE       Log    ${EXECUTED}

Run Keyword with multiple ELSE IF
    Run Keyword If    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE IF    ${True}     Log    ${EXECUTED}
    ...    ELSE       Fail
    Run Keyword If    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE IF    ${True}     Log    ${EXECUTED}
    ...    ELSE IF    ${False}    Fail
    ...    ELSE IF    ${True}     Fail
    ...    ELSE       Fail
    Run Keyword If    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE IF    ${False}    Fail
    ...    ELSE       Log    ${EXECUTED}

Keyword Name in ELSE IF as variable
    ${ret} =    Run Keyword If    ${True}    ${CATENATE}    1    2
    ...    ELSE IF    ${True}    ${FAIL}
    Should Be Equal    ${ret}    1 2
    ${ret} =    Run Keyword If    ${False}    ${FAIL}
    ...    ELSE IF    ${True}    ${CATENATE}    1    2
    Should Be Equal    ${ret}    1 2
    ${ret} =    Run Keyword If    ${False}    ${FAIL}
    ...    ELSE IF    ${False}    ${CATENATE}    1    2
    Should Be Equal    ${ret}    ${None}

Keyword Name in ELSE IF as list variable
    ${ret} =    Run Keyword If    ${0}    ${FAIL}    ELSE IF    ${1}   @{CATENATE STUFF}
    Should Be Equal    ${ret}    1 2 \${escaped} c:\\temp
    ${ret} =    Run Keyword If    ${0}    ${FAIL}    ELSE IF    ${1}   @{EMPTY}    @{CATENATE STUFF}    foo
    Should Be Equal    ${ret}    1 2 \${escaped} c:\\temp foo

Keyword Name in ELSE IF as non-existing variable 1
    [Documentation]    FAIL Variable '\${NON EXISTING}' not found.
    Run Keyword If    ${1}    ${NON EXISTING}    ELSE IF    ${1}    ${FAIL}

Keyword Name in ELSE If as non-existing variable 2
    [Documentation]    FAIL Variable '\${NON EXISTING}' not found.
    Run Keyword If    ${0}    ${FAIL}    ELSE IF    ${1}    ${NON EXISTING}

Keyword Name in ELSE If as non-existing variable 3
    [Documentation]    FAIL Variable '\${NON EXISTING}' not found.
    Run Keyword If    ${0}    ${FAIL}    ELSE IF    ${0}    ${NON EXISTING}

ELSE IF without keyword is invalid 1
    [Documentation]    FAIL ELSE IF requires condition and keyword.
    Run Keyword If    ${True}    Catenate    a1    a2    ELSE IF

ELSE IF without keyword is invalid 2
    [Documentation]    FAIL ELSE IF requires condition and keyword.
    Run Keyword If    ${True}    Catenate    a1    a2    ELSE IF    ${True}

ELSE IF without keyword is invalid 3
    [Documentation]    FAIL ELSE IF requires condition and keyword.
    Run Keyword If    ${False}    Catenate    a1    a2    ELSE IF

ELSE IF without keyword is invalid 4
    [Documentation]    FAIL ELSE IF requires condition and keyword.
    Run Keyword If    ${False}    Catenate    a1    a2    ELSE IF    ${True}

ELSE before ELSE IF is ignored
    Run Keyword If    ${False}    Fail
    ...    ELSE       Fail
    ...    ELSE IF    ${True}     Log    ${EXECUTED}

ELSE and ELSE IF inside list arguments should be escaped
    ${result}=    Run Keyword If    False    Keyword    ELSE IF    @{EXPR AND CATENATE}
    Should be equal    ${result}    \${foo} ELSE IF zig ELSE bar
    ${result}=    Run Keyword If    False    Keyword    ELSE    Catenate    @{EXPR AND CATENATE}
    Should be equal    ${result}    True Catenate \${foo} ELSE IF zig ELSE bar
    ${result}=    Run Keyword If    @{EXPR AND CATENATE}
    Should be equal    ${result}    \${foo} ELSE IF zig ELSE bar

ELSE and ELSE IF must be upper case
    Run Keyword If    ${True}    Log Many    else    ${EXECUTED}
    Run Keyword If    ${True}    Log Many    ELSE iF   ${EXECUTED}

ELSE and ELSE IF must be whitespace sensitive
    Run Keyword If    ${True}    Log Many    EL SE    ${EXECUTED}
    Run Keyword If    ${True}    Log Many    ELSEIF   ${EXECUTED}

Run Keyword With Escaped ELSE and ELSE IF
    Run Keyword If    ${True}    Log Many    \ELSE    ${EXECUTED}
    Run Keyword If    ${True}    Log Many    \ELSE IF   ${EXECUTED}

Run Keyword With ELSE and ELSE IF from Variable
    Run Keyword If    ${True}    Log Many    @{ARGS WITH ELSE}
    Run Keyword If    ${True}    Log Many    @{ARGS WITH ELSE}    ELSE    Fail
    Run Keyword If    ${True}    Log Many    @{ARGS WITH ELSE IF}
    Run Keyword If    ${True}    Log Many    @{ARGS WITH ELSE IF}    ELSE    Fail

Run Keyword Unless With False Expression
    ${empty list} =    Create List
    Run Keyword Unless    ${empty list}    Log    ${EXECUTED}

Run Keyword Unless With True Expression
    Run Keyword Unless    ${0} == ${0}    Log    ${NON EXISTING}


*** Keywords ***
Conditional User Keyword
    [Arguments]    ${status}    ${message}
    Run Keyword If    '${status}' == 'PASS'    Log    ${message}
