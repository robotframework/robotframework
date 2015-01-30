*** Variables ***
@{LIST}       A    B    C    D    E    F    G
${ONE}        1
${INVALID}    xxx

*** Test Cases ***
Valid index
    Should Be Equal    @{LIST}[0]     A
    Should Be Equal    @{LIST}[1]     B
    Should Be Equal    @{LIST}[-1]    G

Valid index using variable
    Should Be Equal    @{LIST}[${0}]      A
    Should Be Equal    @{LIST}[${ONE}]    B
    Should Be Equal    @{LIST}[${-1}]     G

Invalid index
    [Documentation]    FAIL List variable '\@{LIST}' has no item in index 7.
    Log    @{LIST}[7]

Invalid index using variable
    [Documentation]    FAIL List variable '\@{LIST}' has no item in index 12.
    Log    @{LIST}[${ONE}${2}]

Non-string index
    [Documentation]    FAIL List variable '\@{LIST}' used with invalid index 'invalid'.
    Log    @{LIST}[invalid]

Non-string index using variable
    [Documentation]    FAIL List variable '\@{LIST}' used with invalid index 'xxx'.
    Log    @{LIST}[${INVALID}]

Non-existing list variable
    [Documentation]    FAIL Variable '\@{nonex list}' not found.
    Log    @{nonex list}[0]

Non-existing index variable
    [Documentation]    FAIL Variable '\${nonex index}' not found.
    Log    @{LIST}[${nonex index}]
