*** Test Case ***
Variables Set In One Test Are Not Visible In Another 1
    ${test_var} =      Set Variable    Variable in test level
    Set Test Variable    ${test_var_2}    Variable in test level

Variables Set In One Test Are Not Visible In Another 2
    Variable Should Not Exist    $test_var
    Variable Should Not Exist    $test_var_2

Variables do not leak
    ${test}=    Set variable    test
    Keyword should not see local variables
    Variable should not exist    ${kw}
    Should be equal   ${test}    test

Variables can be passed as arguments
    ${test}=    Set variable    test
    ${test}=    Set variable    ${test}
    ${test}=   Keyword should see passed values   ${test}
    Should be equal    ${test}    kw2

Set test variable
    Set test variable    ${test}    test
    Keyword should see test scope variables
    Should be equal   ${test}    kw2
    Should be equal   ${kw}    kw2

*** Keyword ***
Keyword should not see local variables
    Variable should not exist    ${test}
    ${kw}=    Set variable    local
    Keyword should not see local variables 2
    Should be equal   ${kw}    local
    Variable should not exist    ${test}

Keyword should not see local variables 2
    Variable should not exist    ${test}
    Variable should not exist    ${kw}
    ${test}=   Set variable    kw
    ${kw}=   Set variable    kw

Keyword should see passed values
    [Arguments]    ${arg}
    Should be equal   ${arg}    test
    Variable should not exist    ${test}
    ${arg}=   Set variable    kw
    ${arg}=   Keyword should see passed values 2    ${arg}
    [Return]    ${arg}

Keyword should see passed values 2
    [Arguments]    ${arg2}
    Should be equal   ${arg2}    kw
    Variable should not exist    ${test}
    Variable should not exist    ${arg}
    [Return]    kw2

Keyword should see test scope variables
    Should be equal   ${test}    test
    Set test variable   ${test}    kw
    Set test variable   ${kw}    kw
    ${kw}=    Set variable    local
    Should be equal   ${kw}    local
    Keyword should see test scope variables 2
    Should be equal   ${test}    kw2
    Should be equal   ${kw}    kw2
    ${kw}=    Set variable    local
    Should be equal   ${kw}    local

Keyword should see test scope variables 2
    Should be equal   ${test}    kw
    Should be equal   ${kw}    kw
    Set test variable   ${test}    kw2
    Set test variable   ${kw}    kw2
