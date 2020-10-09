*** Settings ***
Library       Collections
Library       XML

*** Variables ***
${INT}        ${15}
&{DICT}       A=1    B=2    C=3    ${1}=${2}    3=4    ${NONE}=${NONE}    =    ${SPACE}=${SPACE}
...           eq=${{{'second': 'xXx', 'ignore_case': True}}}
&{SQUARES}    [=open    ]=close    []=both    [x[y]=mixed
${A}          A
${INVALID}    xxx

*** Test Cases ***
Valid key
    Should Be Equal    ${DICT}[A]     1
    Should Be Equal    ${DICT}[B]     2
    Should Be Equal    ${DICT}[3]     4
    Should Be Equal    ${DICT}[]      ${EMPTY}
    Should Be Equal    ${DICT}[ ]     ${SPACE}

Valid key with square brackets
    Should Be Equal    ${SQUARES}[\[]          open
    Should Be Equal    ${SQUARES}[\]]          close
    Should Be Equal    ${SQUARES}[[]]          both
    Should Be Equal    ${SQUARES}[\[\]]        both
    Should Be Equal    ${SQUARES}[\[x[y]]      mixed
    Should Be Equal    ${SQUARES}[[x\[y]]      mixed
    Should Be Equal    ${SQUARES}[\[x\[y\]]    mixed

Unmatched square brackets 1
    [Documentation]    FAIL Variable item '\${SQUARES}[[]' was not closed properly.
    Log    ${SQUARES}[[]

Unmatched square brackets 2
    [Documentation]    FAIL Variable item '\${SQUARES}[][' was not closed properly.
    Log    ${SQUARES}[][

Unmatched square brackets 3
    [Documentation]    FAIL Variable item '\${SQUARES}[[x[y]]' was not closed properly.
    Log    ${SQUARES}[[x[y]]

Index with variable
    Should Be Equal    ${DICT}[${A}]           1
    Should Be Equal    ${DICT}[${1}]           ${2}
    Should Be Equal    ${DICT}[${NONE}]        ${NONE}
    Should Be Equal    ${DICT}[${EMPTY}]       ${EMPTY}
    Should Be Equal    ${DICT}[A${EMPTY}]      1
    Should Be Equal    ${DICT}[${A}${EMPTY}]   1

Index with variable using item access
    Should Be Equal    ${DICT}[${DICT}[C]]  4
    Should Be Equal    ${DICT}[${A[0]}]     1

Values can be mutated
    @{list} =    Create List    A
    &{dict} =    Create Dictionary    list=${list}
    Set To Dictionary    ${dict}    dict=${dict}
    Append To List    ${list}    B
    Append To List    ${dict}[list]    C
    Set To Dictionary    ${dict}    X=1
    Set To Dictionary    ${dict}[dict]    Y=2
    @{expected} =    Create List    A    B    C
    Lists Should Be Equal    ${dict}[list]    ${expected}
    @{expected} =    Create List    list    dict    X    Y
    Lists Should Be Equal    ${dict}[dict]    ${expected}

List-like values are not manipulated
    ${element} =    Parse XML    <element><child/></element>
    ${tuple} =    Evaluate    (1, 2, 3)
    &{dict} =    Create Dictionary    element=${element}    tuple=${tuple}
    Should Be Equal    ${dict}[element]    ${element}
    Should Be Equal    ${dict}[tuple]    ${tuple}

Integer key cannot be accessed as string
    [Documentation]    FAIL Dictionary '\${DICT}' has no key '1'.
    Log    ${DICT}[1]

String key cannot be accessed as integer
    [Documentation]    FAIL Dictionary '\${DICT}' has no key '3'.
    Log    ${DICT}[${3}]

Invalid key
    [Documentation]    FAIL Dictionary '\${DICT}' has no key 'nonex'.
    Log    ${DICT}[nonex]

Invalid key using variable
    [Documentation]    FAIL Dictionary '\${DICT}' has no key 'xxx'.
    Log    ${DICT}[${INVALID}]

Non-hashable key
    [Documentation]    FAIL STARTS: Dictionary '\${DICT}' used with invalid key:
    Log    ${DICT}[@{DICT}]

Non-existing variable
    [Documentation]    FAIL Variable '\${nonex dict}' not found.
    Log    ${nonex dict}[0]

Non-existing index variable
    [Documentation]    FAIL Variable '\${nonex key}' not found.
    Log    ${DICT}[${nonex key}]

Non-dict variable
    [Documentation]    FAIL
    ...    Variable '\${INT}' is integer, which is not subscriptable, and thus \
    ...    accessing item '0' from it is not possible. To use '[0]' as a \
    ...    literal value, it needs to be escaped like '\\[0]'.
    Log    ${INT}[0]

Sanity check
    @{items} =    Create List
    FOR    ${key}    ${value}    IN    &{DICT}
        Should Be Equal    ${DICT}[${key}]    ${value}
        Append To List    ${items}    ${key}: ${value}
    END
    ${items} =    Catenate    SEPARATOR=,${SPACE}    @{items}
    Should Be Equal    ${items}    A: 1, B: 2, C: 3, 1: 2, 3: 4, None: None, : , ${SPACE}: ${SPACE}, eq: ${DICT}[eq]

Dict expansion using `&` syntax
    [Documentation]    FAIL This fails
    Should Be Equal    XXX    &{DICT}[eq]
    Should Be Equal    &{DICT}[eq]    first=xxx
    Should Be Equal    YYY    &{DICT}[eq]    second=yyy
    Should Be Equal    xxx    values=False    &{DICT}[eq]    ignore_case=False    msg=This fails

Dict expansion fails if value is not dict-like
    [Documentation]    FAIL Value of variable '\&{DICT}[eq][second]' is not dictionary or dictionary-like.
    Log Many    &{DICT}[eq][second]
