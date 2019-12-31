*** Variables ***
${INT}        ${15}
@{LIST}       A    B    C    D    E    F    G    H    I    J    K
@{NUMBERS}    1    2    3
&{MAP}        first=0    last=-1
${ONE}        1
${INVALID}    xxx
${COLON}      :

*** Test Cases ***
Valid index
    Should Be Equal    ${LIST}[0]     A
    Should Be Equal    ${LIST}[1]     B
    Should Be Equal    ${LIST}[-1]    K

Index with variable
    Should Be Equal    ${LIST}[${0}]        A
    Should Be Equal    ${LIST}[${ONE}]      B
    Should Be Equal    ${LIST}[${-1}]       K
    Should Be Equal    ${LIST}[${1}${0}]    K

Index with variable using item access
    Should Be Equal    ${LIST}[${NUMBERS}[2]]    D
    Should Be Equal    ${LIST}[${MAP}[first]]    A
    Should Be Equal    ${LIST}[${MAP}[last]]     K
    Should Be Equal    ${LIST}[${ONE[0]}]        B

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

Slicing with variable
    Should Be Equal    ${LIST}[${1}:]        ${LIST[1:]}
    Should Be Equal    ${LIST}[1${COLON}]    ${LIST[1:]}
    Should Be Equal    ${LIST}[${1}${COLON}${EMPTY}${2}${0}${EMPTY}${0}]
    ...                                      ${LIST[1:]}

Invalid index
    [Documentation]    FAIL Sequence '\${LIST}' has no item in index 12.
    Log    ${LIST}[12]

Invalid index using variable
    [Documentation]    FAIL Sequence '\${LIST}' has no item in index 13.
    Log    ${LIST}[${ONE}${3}]

Non-int index
    [Documentation]    FAIL \
    ...    Sequence '\${LIST}' used with invalid index 'invalid'. To use \
    ...    '[invalid]' as a literal value, it needs to be escaped like \
    ...    '\\[invalid]'.
    Log    ${LIST}[invalid]

Non-int index using variable 1
    [Documentation]    FAIL \
    ...    Sequence '\${LIST}' used with invalid index 'xxx'. To use \
    ...    '[xxx]' as a literal value, it needs to be escaped like '\\[xxx]'.
    Log    ${LIST}[${INVALID}]

Non-int index using variable 2
    [Documentation]    FAIL \
    ...    Sequence '\${LIST}' used with invalid index '1.1'. To use \
    ...    '[1.1]' as a literal value, it needs to be escaped like '\\[1.1]'.
    Log    ${LIST}[${1.1}]

Empty index
    [Documentation]    FAIL \
    ...    Sequence '\${LIST}' used with invalid index ''. To use \
    ...    '[]' as a literal value, it needs to be escaped like '\\[]'.
    Log    ${LIST}[]

Invalid slice
    [Documentation]    FAIL \
    ...    Sequence '\${LIST}' used with invalid index '1:2:3:4'. To use \
    ...    '[1:2:3:4]' as a literal value, it needs to be escaped like \
    ...    '\\[1:2:3:4]'.
    Log    ${LIST}[1:2:3:4]

Non-int slice index 1
    [Documentation]    FAIL \
    ...    Sequence '\${LIST}' used with invalid index 'ooops:'. To use \
    ...    '[ooops:]' as a literal value, it needs to be escaped like \
    ...    '\\[ooops:]'.
    Log    ${LIST}[ooops:]

Non-int slice index 2
    [Documentation]    FAIL \
    ...    Sequence '\${LIST}' used with invalid index '1:ooops'. To use \
    ...    '[1:ooops]' as a literal value, it needs to be escaped like \
    ...    '\\[1:ooops]'.
    Log    ${LIST}[1:ooops]

Non-int slice index 3
    [Documentation]    FAIL \
    ...    Sequence '\${LIST}' used with invalid index '1:2:ooops'. To use \
    ...    '[1:2:ooops]' as a literal value, it needs to be escaped like \
    ...    '\\[1:2:ooops]'.
    Log    ${LIST}[1:2:ooops]

Non-existing variable
    [Documentation]    FAIL Variable '\${nonex list}' not found.
    Log    ${nonex list}[0]

Non-existing index variable
    [Documentation]    FAIL Variable '\${nonex index}' not found.
    Log    ${LIST}[${nonex index}]

Non-subscriptable variable
    [Documentation]    FAIL
    ...    Variable '\${INT}' is integer, which is not subscriptable, and thus \
    ...    accessing item '0' from it is not possible. To use '[0]' as a \
    ...    literal value, it needs to be escaped like '\\[0]'.
    Log    ${INT}[0]

Old syntax with `@` still works but is deprecated
    [Documentation]    `\${list}[1]` and `\@{list}[1]` work same way still.
    ...                In the future latter is deprecated and changed.
    ...                FAIL Sequence '\@{LIST}' has no item in index 99.
    Should Be Equal    @{LIST}[0]         A
    Should Be Equal    @{LIST}[${-1}]     K
    Log    @{LIST}[99]

Old syntax with `@` doesn't support new slicing syntax
    [Documentation]    Slicing support should be added in RF 3.3 when `@{list}[index]` changes.
    ...                FAIL Sequence '\@{LIST}' used with invalid index '1:'. \
    ...                To use '[1:]' as a literal value, it needs to be \
    ...                escaped like '\\[1:]'.
    Log    @{LIST}[1:]
