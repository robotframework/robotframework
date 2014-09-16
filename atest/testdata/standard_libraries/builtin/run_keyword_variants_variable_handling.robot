*** Setting ***
Library           RegisteringLibrary.py
Variables         variable.py

*** Variable ***
@{NEEDS ESCAPING}    c:\\temp\\foo    \${notvar}
@{KEYWORD AND ARG WHICH NEEDS ESCAPING}    \\Log Many    \${notvar}
@{KEYWORD AND ARGS WHICH NEEDS ESCAPING}    \\Log Many    @{NEEDS ESCAPING}
@{EMPTY}
@{KEYWORD}        \\Log Many
@{EXPRESSION}     ${TRUE}
@{ARGS}           @{NEEDS ESCAPING}
${KEYWORD}        \\Log Many

*** Test Case ***
Variable Values Should Not Be Visible As Keyword's Arguments
    Run Keyword    My UK    Log    ${OBJECT}

Run Keyword When Keyword and Arguments Are in List Variable
    Run Keyword    @{KEYWORD AND ARGS WHICH NEEDS ESCAPING}
    Run Keyword    @{KEYWORD AND ARG WHICH NEEDS ESCAPING}

Run Keyword If When Arguments are In Multiple List
    Run Keyword If    @{EXPRESSION}    @{KEYWORD}    @{ARGS}

Run Keyword When Arguments are Not In First Lists
    Run Keyword    @{EMPTY}    @{EMPTY}    @{EMPTY}    @{KEYWORD}    @{ARGS}

Run Keyword When Keyword And Arguments In Scalar After Empty Lists
    Run Keyword    @{EMPTY}    @{EMPTY}    ${KEYWORD}    @{ARGS}

Run Keyword When Keyword And String Arguments After Empty Lists
    [Documentation]    FAIL Expected Failure
    Run Keyword    @{EMPTY}    @{EMPTY}    Fail    Expected Failure

Run Keyword If When Not Enough Arguments
    [Documentation]    FAIL Keyword 'BuiltIn.Run Keyword If' expected at least 2 arguments, got 1.
    Run Keyword If    @{EMPTY}    @{EMPTY}    @{EMPTY}    @{EXPRESSION}

Run Keyword When Run Keyword Does Not Take Keyword
    Run Keyword Without Keyword    @{ARGS}

Run Keyword If With List And Two Arguments That needs to Be Processed
    Run Keyword If    @{EMPTY}    ${TRUE}    \\Log Many    @{ARGS}

Run Keyword If With List And One Argument That needs to Be Processed
    Run Keyword If    @{EXPRESSION}    \\Log Many    @{ARGS}

*** Keyword ***
My UK
    [Arguments]    ${name}    @{args}
    Run Keyword    ${name}    @{args}

\Log Many
    [Arguments]    @{args}
    Log Many    @{args}
