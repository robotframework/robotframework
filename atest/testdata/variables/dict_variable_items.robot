*** Settings ***
Library       Collections
Library       XML

*** Variables ***
&{DICT}       A=1    B=2    C=3    ${1}=${2}    3=4    ${NONE}=${NONE}  =
${A}          A
${INVALID}    xxx

*** Test Cases ***
Valid key
    Should Be Equal    ${DICT}[A]     1
    Should Be Equal    ${DICT}[B]     2
    Should Be Equal    ${DICT}[3]     4
    Should Be Equal    ${DICT}[]      ${EMPTY}

Valid index using variable
    Should Be Equal    ${DICT}[${A}]        1
    Should Be Equal    ${DICT}[${1}]        ${2}
    Should Be Equal    ${DICT}[${NONE}]     ${NONE}
    Should Be Equal    ${DICT}[${EMPTY}]    ${EMPTY}

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
    ...    Variable '\${INVALID}' is string, not list or dictionary,\
    ...    and thus accessing item '${nonex}' from it is not possible.
    Log    ${INVALID}[${nonex}]

Sanity check
    @{items} =    Create List
    :FOR    ${key}    IN    @{DICT}
    \    Append To List    ${items}    ${key}: ${DICT}[${key}]
    ${items} =    Catenate    SEPARATOR=,${SPACE}    @{items}
    Should Be Equal    ${items}    A: 1, B: 2, C: 3, 1: 2, 3: 4, None: None, :${SPACE}

Old syntax with `&` still works like earlier
    [Documentation]    FAIL Dictionary '\&{DICT}' has no key 'nonex'.
    Should Be Equal    &{DICT}[A]     1
    Should Be Equal    &{DICT}[${1}]        ${2}
    Log    &{DICT}[nonex]
