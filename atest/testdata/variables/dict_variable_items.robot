*** Settings ***
Library       Collections

*** Variables ***
&{DICT}       A=1    B=2    C=3    ${1}=${2}    3=4    ${NONE}=${NONE}  =
${A}          A
${INVALID}    xxx

*** Test Cases ***
Valid key
    Should Be Equal    &{DICT}[A]     1
    Should Be Equal    &{DICT}[B]     2
    Should Be Equal    &{DICT}[3]     4
    Should Be Equal    &{DICT}[]      ${EMPTY}

Valid index using variable
    Should Be Equal    &{DICT}[${A}]        1
    Should Be Equal    &{DICT}[${1}]        ${2}
    Should Be Equal    &{DICT}[${NONE}]     ${NONE}
    Should Be Equal    &{DICT}[${EMPTY}]    ${EMPTY}

Integer key cannot be accessed as string
    [Documentation]    FAIL Dictionary variable '\&{DICT}' has no key '1'.
    Log    &{DICT}[1]

String key cannot be accessed as integer
    [Documentation]    FAIL Dictionary variable '\&{DICT}' has no key '3'.
    Log    &{DICT}[${3}]

Invalid key
    [Documentation]    FAIL Dictionary variable '\&{DICT}' has no key 'nonex'.
    Log    &{DICT}[nonex]

Invalid key using variable
    [Documentation]    FAIL Dictionary variable '\&{DICT}' has no key 'xxx'.
    Log    &{DICT}[${INVALID}]

Non-hashable key
    [Documentation]    FAIL STARTS: Dictionary variable '\&{DICT}' used with invalid key:
    Log    &{DICT}[@{DICT}]

Non-existing dict variable
    [Documentation]    FAIL Variable '\&{nonex dict}' not found.
    Log    &{nonex dict}[0]

Non-existing index variable
    [Documentation]    FAIL Variable '\${nonex key}' not found.
    Log    &{DICT}[${nonex key}]

Sanity check
    @{items} =    Create List
    :FOR    ${key}    IN    @{DICT}
    \    Append To List    ${items}    ${key}: &{DICT}[${key}]
    ${items} =    Catenate    SEPARATOR=,${SPACE}    @{items}
    Should Be Equal    ${items}    A: 1, B: 2, C: 3, 1: 2, 3: 4, None: None, :${SPACE}
