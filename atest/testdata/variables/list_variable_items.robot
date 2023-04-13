*** Settings ***
Variables         list_variable_items.py

*** Variables ***
${INT}            ${15}
@{LIST}           A    B    C    D    E    F    G    H    I    J    K
@{NUMBERS}        1    2    3
@{NESTED}         ${{['a', 'b', 'c']}}    ${{[1, 2, 3]}}
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
    ...    To use '[]' as a literal value, it needs to be escaped like '\\[]'.
    Log    ${BYTES}[]

Invalid slice list
    [Documentation]    FAIL
    ...    List '\${LIST}' used with invalid index '1:2:3:4'. \
    ...    To use '[1:2:3:4]' as a literal value, it needs to be escaped like '\\[1:2:3:4]'.
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

List expansion using `@` syntax
    [Documentation]    FAIL List '\@{NESTED}' has no item in index 99.
    ${result} =    Catenate    @{NESTED}[0]    -    @{NESTED}[${-1}]
    Should Be Equal    ${result}    a b c - 1 2 3
    Log Many    @{NESTED}[99]

List expansion fails if value is not list-like 1
    [Documentation]    FAIL Value of variable '\@{LIST}[0]' is not list or list-like.
    Log Many    @{LIST}[0]

List expansion fails if value is not list-like 2
    [Documentation]    FAIL Value of variable '\@{NESTED}[1][0]' is not list or list-like.
    Log Many    @{NESTED}[1][0]

List expansion with slice
    ${result} =    Catenate    @{LIST}[7:]    -    @{LIST}[:${3}]    -    @{LIST}[8:2:-3]
    Should Be Equal    ${result}    H I J K - A B C - I F
    ${result} =    Catenate    @{NESTED}[0][1:]    -    @{NESTED}[:][${-1}][::][${99}:-99:-2][:99:1]
    Should Be Equal    ${result}    b c - 3 1

List expansion with slice fails if value is not list-like
    [Documentation]    FAIL Value of variable '\@{STRING}[1:]' is not list or list-like.
    Log Many    @{STRING}[1:]

Object supporting both index and key access
    Valid index              ${MIXED USAGE}
    Index with variable      ${MIXED USAGE}
    Slicing                  ${MIXED USAGE}
    Slicing with variable    ${MIXED USAGE}
    Should be equal          ${MIXED USAGE}[A]    ${0}
    Should be equal          ${MIXED USAGE}[K]    ${10}
    Run keyword and expect error
    ...    EQUALS: MixedUsage '\${MIXED USAGE}' has no item in index 11.
    ...    Log    ${MIXED USAGE}[11]
    Run keyword and expect error
    ...    STARTS: Accessing '\${MIXED USAGE}[X]' failed: ValueError:
    ...    Log    ${MIXED USAGE}[X]
    Run keyword and expect error
    ...    EQUALS: MixedUsage '\${MIXED USAGE}' used with invalid index 'None'. To use '[None]' as a literal value, it needs to be escaped like '\\[None]'.
    ...    Log    ${MIXED USAGE}[${NONE}]

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
    Should Be Equal    ${sequence}[:][1:]     ${sequence[1:]}
    Should Be Equal    ${sequence}[:][::]     ${sequence}
    Should Be Empty    ${sequence}[100:]

Slicing with variable
    [Arguments]        ${sequence}
    Should Be Equal    ${sequence}[${1}:]            ${sequence[1:]}
    Should Be Equal    ${sequence}[${{slice(1)}}]    ${sequence[:1]}
    Should Be Equal    ${sequence}[${1}${COLON}${EMPTY}${2}${0}${EMPTY}${0}]
    ...                                              ${sequence[1:]}
