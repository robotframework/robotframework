*** Setting ***
Library           RegisteringLibrary.py
Library           NotRegisteringLibrary.py
Library           RegisteringLibrary.py    WITH NAME    lib
Library           RegisteredClass.py
Library           DynamicRegisteredLibrary.py

*** Variable ***
${VARIABLE}       \${not variable}
${HELLO}          Hello
@{KEYWORD AND ARG}    \\Log Many    ${VARIABLE}

*** Test Case ***
Not registered Keyword Fails With Content That Should Not Be Evaluated Twice
    [Documentation]    FAIL Non-existing variable '\${not variable}'.
    ${var} =    Set Variable    \${not variable}
    Should Be Equal    ${var}    \${not variable}
    My Run Keyword    Log    ${HELLO}
    My Run Keyword    Log    ${VARIABLE}

Registered Function
    ${var} =    RegisteringLibrary.Run Keyword Function    Set Variable    ${VARIABLE}
    Should Be Equal    ${var}    \${not variable}

Registered Method
    ${var} =    Run Keyword If Method    ${TRUE}    Set Variable    ${VARIABLE}
    Should Be Equal    ${var}    \${not variable}

With Name And Args To Process Registered Method
    ${var} =    Run KeywordMethod    Set Variable    ${VARIABLE}
    Should Be Equal    ${var}    \${not variable}

Registered Keyword With With Name
    ${var} =    lib.Run Keyword Function    Set Variable    ${VARIABLE}
    Should Be Equal    ${var}    \${not variable}

Registered Keyword From Dynamic Library
    Dynamic Run Keyword    @{KEYWORD AND ARG}

*** Keyword ***
\Log Many
    [Arguments]    @{args}
    Log Many    @{args}
