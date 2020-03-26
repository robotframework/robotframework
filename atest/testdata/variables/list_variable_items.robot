*** Variables ***
${INT}            ${15}
@{LIST}           A    B    C    D    E    F    G    H    I    J    K
@{NUMBERS}        1    2    3
${BYTES}          ${{b'ABCDEFGHIJK'}}
${BYTEARRAY}      ${{bytearray(b'ABCDEFGHIJK')}}
${STRING}         ABCDEFGHIJK
&{MAP}            first=0    last=-1
${ONE}            1
${INVALID}        xxx
${COLON}          :
${BYTES NAME}     ${{'Bytes' if not isinstance(b'', str) else 'String'}}

*** Test Cases ***
Valid index
    Valid index    ${LIST}
    Valid index    ${STRING}
    Should Be Equal    ${BYTES}[0]    ${{b'ABCDEFGHIJK'[0]}}
    Should Be Equal    ${BYTES}[-1]    ${{b'ABCDEFGHIJK'[-1]}}

Index with variable
    Index with variable    ${LIST}
    Index with variable    ${STRING}
    Should Be Equal    ${BYTES}[${0}]    ${{b'A'[0]}}
    Should Be Equal    ${BYTES}[${-1}]    ${{b'K'[0]}}

Index with variable using item access
    Index with variable using item access    ${LIST}
    Index with variable using item access    ${STRING}

Slicing
    Slicing            ${LIST}
    Slicing            ${STRING}
    Slicing            ${BYTES}
    Slicing            ${BYTEARRAY}

Slicing with variable
    Slicing with variable    ${LIST}
    Slicing with variable    ${STRING}
    Slicing with variable    ${BYTES}
    Slicing with variable    ${BYTEARRAY}

Invalid index list
    [Documentation]    FAIL List '\${LIST}' has no item in index 12.
    Log    ${LIST}[12]

Invalid index string
    [Documentation]    FAIL String '\${STRING}' has no item in index 12.
    Log    ${STRING}[12]

Invalid index bytes
    [Documentation]    FAIL ${BYTES NAME} '\${BYTES}' has no item in index 12.
    Log    ${BYTES}[12]

Invalid index using variable
    [Documentation]    FAIL List '\${LIST}' has no item in index 13.
    Log    ${LIST}[${ONE}${3}]

Non-int index list
    [Documentation]    FAIL
    ...    List '\${LIST}' used with invalid index 'invalid'. \
    ...    To use '[invalid]' as a literal value, it needs to be escaped like '\\[invalid]'.
    Log    ${LIST}[invalid]

Non-int index string
    [Documentation]    FAIL
    ...    String '\${STRING}' used with invalid index 'invalid'. \
    ...    To use '[invalid]' as a literal value, it needs to be escaped like '\\[invalid]'.
    Log    ${STRING}[invalid]

Non-int index bytes
    [Documentation]    FAIL
    ...    ${BYTES NAME} '\${BYTES}' used with invalid index 'invalid'. \
    ...    To use '[invalid]' as a literal value, it needs to be escaped like '\\[invalid]'.
    Log    ${BYTES}[invalid]

Non-int index using variable 1
    [Documentation]    FAIL
    ...    List '\${LIST}' used with invalid index 'xxx'. \
    ...    To use '[xxx]' as a literal value, it needs to be escaped like '\\[xxx]'.
    Log    ${LIST}[${INVALID}]

Non-int index using variable 2
    [Documentation]    FAIL
    ...    List '\${LIST}' used with invalid index '1.1'. \
    ...    To use '[1.1]' as a literal value, it needs to be escaped like '\\[1.1]'.
    Log    ${LIST}[${1.1}]

Empty index list
    [Documentation]    FAIL
    ...    List '\${LIST}' used with invalid index ''. \
    ...    To use '[]' as a literal value, it needs to be escaped like '\\[]'.
    Log    ${LIST}[]

Empty index string
    [Documentation]    FAIL
    ...    String '\${STRING}' used with invalid index ''. \
    ...    To use '[]' as a literal value, it needs to be escaped like '\\[]'.
    Log    ${STRING}[]

Empty index bytes
    [Documentation]    FAIL
    ...    ${BYTES NAME} '\$\{BYTES}' used with invalid index ''. \
    ...     To use '[]' as a literal value, it needs to be escaped like '\\[]'.
    Log    ${BYTES}[]

Invalid slice list
    [Documentation]    FAIL
    ...    List '\${LIST}' used with invalid index '1:2:3:4'. \
    ...    To use  '[1:2:3:4]' as a literal value, it needs to be escaped like '\\[1:2:3:4]'.
    Log    ${LIST}[1:2:3:4]

Invalid slice string
    [Documentation]    FAIL
    ...    String '\${STRING}' used with invalid index '1:2:3:4'. \
    ...    To use '[1:2:3:4]' as a literal value, it needs to be escaped like '\\[1:2:3:4]'.
    Log    ${STRING}[1:2:3:4]

Invalid slice bytes
    [Documentation]    FAIL
    ...    ${BYTES NAME} '\${BYTES}' used with invalid index '1:2:3:4'. \
    ...    To use '[1:2:3:4]' as a literal value, it needs to be escaped like '\\[1:2:3:4]'.
    Log    ${BYTES}[1:2:3:4]

Non-int slice index 1
    [Documentation]    FAIL
    ...    List '\${LIST}' used with invalid index 'ooops:'. \
    ...    To use '[ooops:]' as a literal value, it needs to be escaped like '\\[ooops:]'.
    Log    ${LIST}[ooops:]

Non-int slice index 2
    [Documentation]    FAIL \
    ...    List '\${LIST}' used with invalid index '1:ooops'. \
    ...    To use '[1:ooops]' as a literal value, it needs to be escaped like '\\[1:ooops]'.
    Log    ${LIST}[1:ooops]

Non-int slice index 3
    [Documentation]    FAIL \
    ...    List '\${LIST}' used with invalid index '1:2:ooops'. \
    ...    To use '[1:2:ooops]' as a literal value, it needs to be escaped like '\\[1:2:ooops]'.
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
    ...                FAIL List '\@{LIST}' has no item in index 99.
    Should Be Equal    @{LIST}[0]         A
    Should Be Equal    @{LIST}[${-1}]     K
    Log    @{LIST}[99]

Old syntax with `@` doesn't support new slicing syntax
    [Documentation]    Slicing support should be added in RF 3.3 when `@{list}[index]` changes.
    ...                FAIL List '\@{LIST}' used with invalid index '1:'. \
    ...                To use '[1:]' as a literal value, it needs to be \
    ...                escaped like '\\[1:]'.
    Log    @{LIST}[1:]

*** Keywords ***
Valid index
    [Arguments]        ${sequence}
    Should Be Equal    ${sequence}[0]     A
    Should Be Equal    ${sequence}[1]     B
    Should Be Equal    ${sequence}[-1]    K

Index with variable
    [Arguments]        ${sequence}
    Should Be Equal    ${sequence}[${0}]        A
    Should Be Equal    ${sequence}[${ONE}]      B
    Should Be Equal    ${sequence}[${-1}]       K
    Should Be Equal    ${sequence}[${1}${0}]    K

Index with variable using item access
    [Arguments]        ${sequence}
    Should Be Equal    ${sequence}[${NUMBERS}[2]]    D
    Should Be Equal    ${sequence}[${MAP}[first]]    A
    Should Be Equal    ${sequence}[${MAP}[last]]     K
    Should Be Equal    ${sequence}[${ONE[0]}]        B

Slicing
    [Arguments]        ${sequence}
    Should Be Equal    ${sequence}[1:]        ${sequence[1:]}
    Should Be Equal    ${sequence}[:2]        ${sequence[:2]}
    Should Be Equal    ${sequence}[::-1]      ${sequence[::-1]}
    Should Be Equal    ${sequence}[1::]       ${sequence[1::]}
    Should Be Equal    ${sequence}[:2:]       ${sequence[:2:]}
    Should Be Equal    ${sequence}[1:2:]      ${sequence[1:2:]}
    Should Be Equal    ${sequence}[:3:2]      ${sequence[:3:2]}
    Should Be Equal    ${sequence}[1:-1:2]    ${sequence[1:-1:2]}
    Should Be Equal    ${sequence}[:]         ${sequence}
    Should Be Equal    ${sequence}[::]        ${sequence}
    Should Be Empty    ${sequence}[100:]

Slicing with variable
    [Arguments]        ${sequence}
    Should Be Equal    ${sequence}[${1}:]        ${sequence[1:]}
    Should Be Equal    ${sequence}[1${COLON}]    ${sequence[1:]}
    Should Be Equal    ${sequence}[${1}${COLON}${EMPTY}${2}${0}${EMPTY}${0}]
    ...                                          ${sequence[1:]}
