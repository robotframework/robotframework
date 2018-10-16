*** Variables ***
@{LIST}       A    B    C    D    E    F    G
${ONE}        1
${INVALID}    xxx

*** Test Cases ***
Valid index
    Should Be Equal    ${LIST}[0]     A
    Should Be Equal    ${LIST}[1]     B
    Should Be Equal    ${LIST}[-1]    G

Valid index using variable
    Should Be Equal    ${LIST}[${0}]      A
    Should Be Equal    ${LIST}[${ONE}]    B
    Should Be Equal    ${LIST}[${-1}]     G

Slicing
    Should Be Equal    ${LIST}[1:]        ${LIST[1:]}
    Should Be Equal    ${LIST}[:2]        ${LIST[:2]}
    Should Be Equal    ${LIST}[::-1]      ${LIST[::-1]}
    Should Be Equal    ${LIST}[1::]       ${LIST[1::]}
    Should Be Equal    ${LIST}[:2:]       ${LIST[:2:]}
    Should Be Equal    ${LIST}[1:2:]      ${LIST[1:2:]}
    Should Be Equal    ${LIST}[:3:2]      ${LIST[:3:2]}
    Should Be Equal    ${LIST}[1:-1:2]    ${LIST[1:-1:2]}
    Should Be Equal    ${LIST}[:]         ${LIST}
    Should Be Equal    ${LIST}[::]        ${LIST}
    Should Be Empty    ${LIST}[100:]

Invalid index
    [Documentation]    FAIL List '\${LIST}' has no item in index 7.
    Log    ${LIST}[7]

Invalid index using variable
    [Documentation]    FAIL List '\${LIST}' has no item in index 12.
    Log    ${LIST}[${ONE}${2}]

Non-int index
    [Documentation]    FAIL List '\${LIST}' used with invalid index 'invalid'.
    Log    ${LIST}[invalid]

Non-int index using variable 1
    [Documentation]    FAIL List '\${LIST}' used with invalid index 'xxx'.
    Log    ${LIST}[${INVALID}]

Non-int index using variable 2
    [Documentation]    FAIL List '\${LIST}' used with invalid index '1.1'.
    Log    ${LIST}[${1.1}]

Empty index
    [Documentation]    FAIL List '\${LIST}' used with invalid index ''.
    Log    ${LIST}[]

Invalid slice
    [Documentation]    FAIL List '\${LIST}' used with invalid index '1:2:3:4'.
    Log    ${LIST}[1:2:3:4]

Non-int slice index 1
    [Documentation]    FAIL List '\${LIST}' used with invalid index 'ooops:'.
    Log    ${LIST}[ooops:]

Non-int slice index 2
    [Documentation]    FAIL List '\${LIST}' used with invalid index '1:ooops'.
    Log    ${LIST}[1:ooops]

Non-int slice index 3
    [Documentation]    FAIL List '\${LIST}' used with invalid index '1:2:ooops'.
    Log    ${LIST}[1:2:ooops]

Non-existing variable
    [Documentation]    FAIL Variable '\${nonex list}' not found.
    Log    ${nonex list}[0]

Non-existing index variable
    [Documentation]    FAIL Variable '\${nonex index}' not found.
    Log    ${LIST}[${nonex index}]

Non-list variable
    [Documentation]    FAIL
    ...    Variable '\${INVALID}' is string, not list or dictionary,\
    ...    and thus accessing item '0' from it is not possible.
    Log    ${INVALID}[0]

Old syntax with `@` still works like earlier
    [Documentation]    `${list}[1]` and `@{list}[1]` work same way still.
    ...                In the future latter is deprecated and changed.
    ...                FAIL List '\@{LIST}' has no item in index 10.
    Should Be Equal    @{LIST}[0]         A
    Should Be Equal    @{LIST}[${-1}]     G
    Log    @{LIST}[10]

Old syntax with `@` doesn't support new slicing syntax
    [Documentation]    Slicing support should be added in RF 3.3 when `@{list}[index]` changes.
    ...                FAIL List '\@{LIST}' used with invalid index '1:'.
    Log    @{LIST}[1:]
