*** Variables ***
@{LIST}          k1    v1    k2    v2    k3    v3
&{DICT}          a=1    b=${2}    ${3}=c
${EQUALS}        foo=bar

*** Test Cases ***
Empty
    &{d} =    Create Dictionary
    Verify Dictionary    ${d}    {}

Separate keys and values
    &{d} =    Create Dictionary    a    1    b    ${2}    c    ${DICT}
    Verify Dictionary    ${d}    {'a': '1', 'b': 2, 'c': {'a': '1', 'b': 2, 3: 'c'}}
    &{d} =    Create Dictionary    k    1    k    2    k    3    k    4
    Verify Dictionary    ${d}    {'k': '4'}

Separate keys and values using non-string keys
    &{d} =    Create Dictionary    ${42}    42    ${NONE}    None
    Verify Dictionary    ${d}    {42: '42', None: 'None'}

Separate keys and values using list variables
    &{d} =    Create Dictionary    @{LIST}    @{EMPTY}    @{DICT}     xxx
    Verify Dictionary    ${d}    {'k1': 'v1', 'k2': 'v2', 'k3': 'v3', 'a': 'b', 3: 'xxx'}
    &{d} =    Create Dictionary    k1    overridden    @{LIST}    k3    overrides
    Verify Dictionary    ${d}    {'k1': 'v1', 'k2': 'v2', 'k3': 'overrides'}

Separate keys and values with escaped equals
    &{d} =    Create Dictionary    escaped\=in\=key    and\=in\\\=value
    Verify Dictionary    ${d}    {'escaped=in=key': r'and=in\\=value'}

Separate keys and values with equals in variable value
    &{d} =    Create Dictionary    ${EQUALS}    ${EQUALS}
    Verify Dictionary    ${d}    {'foo=bar': 'foo=bar'}

Separate keys and values with non-existing variables
    [Documentation]    FAIL Variable '\${NONEX VALUE}' not found.
    Create Dictionary    key    ${NONEX VALUE}

Wrong number of separate keys and values 1
    [Documentation]    FAIL Expected even number of keys and values, got 3.
    Create Dictionary    1    2    3

Wrong number of separate keys and values 2
    [Documentation]    FAIL Expected even number of keys and values, got 7.
    Create Dictionary    @{LIST}    ooops

Separate keys and values with invalid key
    [Documentation]    FAIL STARTS: TypeError:
    Create Dictionary    ${DICT}    non-hashable

`key=value` syntax
    &{d} =    Create Dictionary    a=1    b=2    c=${3}
    Verify Dictionary    ${d}    {'a': '1', 'b': '2', 'c': 3}

`key=value` syntax with non-string keys
    &{d} =    Create Dictionary    ${1}=1    ${2.2}=2.2    ${NONE}=None
    Verify Dictionary    ${d}    {1: '1', 2.2: '2.2', None: 'None'}

`key=value` syntax with escaped equals
    &{d} =    Create Dictionary    esc\=key=esc\=value    bs\\\=\\=value
    Verify Dictionary    ${d}    {'esc=key': 'esc=value', 'bs\\\\=\\\\': 'value'}

`key=value` syntax with equals in variable value
    &{d} =    Create Dictionary    ${EQUALS}=${EQUALS}
    Verify Dictionary    ${d}    {'foo=bar': 'foo=bar'}

`key=value` syntax with non-existing variables 1
    [Documentation]    FAIL Variable '\${NONEX VALUE}' not found.
    Create Dictionary    key=${NONEX VALUE}

`key=value` syntax with non-existing variables 2
    [Documentation]    FAIL Variable '\${NONEX KEY}' not found.
    Create Dictionary    ${NONEX KEY}=${NONEX VALUE}

`key=value` syntax with invalid key
    [Documentation]    FAIL STARTS: Creating dictionary variable failed:
    Create Dictionary    ${DICT}=non-hashable

`key=value` syntax without equals
    [Documentation]    FAIL
    ...    Invalid dictionary variable item 'no'. \
    ...    Items must use 'name=value' syntax or be dictionary variables themselves.
    Create Dictionary    a=1   no   equals

Separate keys and values and 'key=value' syntax
    &{d} =    Create Dictionary   a    ${1}    b    foo    c=3
    Verify Dictionary    ${d}    {'a': 1, 'b': 'foo', 'c': '3'}
    &{d} =    Create Dictionary    k    1    k    2    k=3    k=4
    Verify Dictionary    ${d}    {'k': '4'}

`\&{dict}` variable
    &{d} =    Create Dictionary    &{EMPTY}
    Verify Dictionary    ${d}    {}
    &{d} =    Create Dictionary    &{DICT}
    Verify Dictionary    ${d}    {'a': '1', 'b': 2, 3: 'c'}
    &{d} =    Create Dictionary    &{EMPTY}    &{DICT}    &{EMPTY}    new=item
    Verify Dictionary    ${d}    {'a': '1', 'b': 2, 3: 'c', 'new': 'item'}
    &{d} =    Create Dictionary    &{d}    a=overridded    &{DICT}    b=overrides    another=new
    Verify Dictionary    ${d}    {'a': '1', 'b': 'overrides', 3: 'c', 'new': 'item', 'another': 'new'}

`\&{dict}` variable with internal variables
    ${name} =    Set Variable    DICT
    &{d} =    Create Dictionary    &{${name}}
    Verify Dictionary    ${d}    {'a': '1', 'b': 2, 3: 'c'}
    &{d} =    Create Dictionary    &{${name[${0}]}ic${name[${-1}]}}
    ...    &{${name.lower()}.fromkeys([${4}], '${40 + ${2}}')}
    Verify Dictionary    ${d}    {'a': '1', 'b': 2, 3: 'c', 4: '42'}

Non-existing `\&{dict}` variable
    [Documentation]    FAIL Variable '\&{NONEX}' not found.
    Create Dictionary    &{EMPTY}    &{NONEX}

Non-dictionary `\&{dict}` variable
    [Documentation]    FAIL Value of variable '&{LIST}' is not dictionary or dictionary-like.
    Create Dictionary   &{LIST}    &{NONEX}

*** Keywords ***
Verify Dictionary
    [Arguments]    ${result}    ${expected}
    ${expected} =    Evaluate    ${expected}
    Should Be Equal    ${result}    ${expected}
