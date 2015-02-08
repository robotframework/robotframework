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

Non-int index
    [Documentation]    FAIL List variable '\@{LIST}' used with invalid index 'invalid'.
    Log    @{LIST}[invalid]

Non-int index using variable 1
    [Documentation]    FAIL List variable '\@{LIST}' used with invalid index 'xxx'.
    Log    @{LIST}[${INVALID}]

Non-int index using variable 2
    [Documentation]    FAIL List variable '\@{LIST}' used with invalid index '1.1'.
    Log    @{LIST}[${1.1}]

Empty index
    [Documentation]    FAIL List variable '\@{LIST}' used with invalid index ''.
    Log    @{LIST}[]

Non-existing list variable
    [Documentation]    FAIL Variable '\@{nonex list}' not found.
    Log    @{nonex list}[0]

Non-existing index variable
    [Documentation]    FAIL Variable '\${nonex index}' not found.
    Log    @{LIST}[${nonex index}]
