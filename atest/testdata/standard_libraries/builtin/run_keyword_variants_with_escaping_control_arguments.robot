*** Variables ***
@{RUN KWS ARGS}      Logging keyword    AND    Non-existing and not used keyword
@{RUN KWS}           Run Keywords    @{RUN KWS ARGS}
@{RUN KW IF ARGS}    ${FALSE}    Fail    Not executed
...                  ELSE IF    ${FALSE}    Fail    Not executed
...                  ELSE    Fail    Not executed
@{RUN KW IF}         Run Keyword If    @{RUN KW IF ARGS}
@{RUN KW IF FAIL ARGS}    ${TRUE}    Fail    Expected failure
@{RUN KW IF FAIL}    Run Keyword If    @{RUN KW IF FAIL ARGS}

*** Test Cases ***
Run Keyword with Run Keywords With Arguments Inside List variable should escape AND
    [Documentation]    FAIL No keyword with name 'AND' found.
    Run Keyword    Run Keywords    @{RUN KWS ARGS}

Run Keyword with Run Keywords And Arguments Inside List variable should escape AND
    [Documentation]    FAIL No keyword with name 'AND' found.
    Run Keyword    @{RUN KWS}

Run Keyword If with Run Keywords With Arguments Inside List variable should escape AND
    [Documentation]    FAIL No keyword with name 'AND' found.
    Run Keyword If    ${TRUE}    Run Keywords    @{RUN KWS ARGS}

Run Keyword If with Run Keywords And Arguments Inside List variable should escape AND
    [Documentation]    FAIL No keyword with name 'AND' found.
    Run Keyword If    ${TRUE}    Run Keyword    @{RUN KWS}

Run Keywords With Run Keyword If should not escape ELSE and ELSE IF
    [Documentation]    FAIL Expected failure
    Run Keywords
    ...    Run Keyword If    ${FALSE}    Fail    Not executed
    ...    ELSE IF    ${FALSE}    Fail    Not executed
    ...    ELSE    Log    log message
    ...    AND    Log    that
    ...    AND    Run Keyword If    ${TRUE}    Fail    Expected failure
    ...    ELSE IF    ${TRUE}    Fail    Not executed
    ...    ELSE    Fail    Not executed

Run Keywords With Run Keyword If In List Variable Should Escape ELSE and ELSE IF From List Variable
    [Documentation]    FAIL Expected failure
    Run Keywords
    ...    @{RUN KW IF}
    ...    AND    Log    that
    ...    AND    @{RUN KW IF FAIL}

Run Keywords With Run Keyword If With Arguments From List Variable should escape ELSE and ELSE IF From List Variable
    [Documentation]    FAIL Expected failure
    Run Keywords
    ...    Run Keyword If    @{RUN KW IF ARGS}
    ...    AND    Log    that
    ...    AND    Run Keyword If    @{RUN KW IF FAIL ARGS}

*** Keywords ***
Logging keyword
    Log    log message
