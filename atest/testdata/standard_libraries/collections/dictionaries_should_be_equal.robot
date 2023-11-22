*** Settings ***
Library           Collections
Library           CollectionsHelperLibrary.py

*** Variables ***
@{LIST}          a    B
${TUPLE}         ${{'a', 'B'}}
&{D0}
&{D1}            a=x
&{D2}            a=x    b=y
&{D3}            a=x    b=y    c=${3}
&{D3B}           a=b    b=y    c=3
&{D3C}           A=X    b=Y    C=${3}
&{D9A}           a=1    b=2    c=3    d=4    e=5    f=6    g=7    h=8    i=9
&{D9B}           d=4    e=5    i=9    a=1    f=6    g=7    b=2    h=8    c=3
&{DX}            a=x    B=Y    c=${3}   ${4}=E    ß=Straße
...              list=${LIST}    ${TUPLE}=tuple    dict=${D2}
@{DICTS}         ${D0}    ${D1}    ${D2}    ${D3}    ${D3B}    ${D3C}    ${D9A}    ${D9B}    ${DX}

*** Test Cases ***
Comparison with itself
    FOR    ${d}    IN    @{DICTS}
        Dictionaries Should Be Equal    ${d}    ${d}
    END

Keys in different order
    Dictionaries Should Be Equal    ${D9A}    ${D9B}

Different dictionary types
    FOR    ${d}    IN    @{DICTS}
        Dictionaries Should Be Equal    ${d}    ${{collections.OrderedDict($d)}}
        Dictionaries Should Be Equal    ${{collections.OrderedDict($d)}}    ${d}
    END
    Dictionaries Should Be Equal    ${D9A}    ${{collections.OrderedDict($D9B)}}
    Dictionaries Should Be Equal    ${{collections.OrderedDict($D9A)}}    ${D9B}

First dictionary missing keys
    [Documentation]    FAIL    Following keys missing from first dictionary: 'c'
    Dictionaries Should Be Equal    ${D2}    ${D3}

Second dictionary missing keys
    [Documentation]    FAIL    Following keys missing from second dictionary: 'a' and 'b'
    Dictionaries Should Be Equal    ${D2}    ${D0}

Both dictionaries missing keys
    [Documentation]    FAIL
    ...    Following keys missing from first dictionary: 'c' and 'd'
    ...    Following keys missing from second dictionary: 'b'
    Dictionaries Should Be Equal    ${D2}    ${{{'a': 1, 'c': 3, 'd': 4}}}

Missing keys and custom error message
    [Documentation]    FAIL    The error.
    Dictionaries Should Be Equal    ${D2}    ${D3}    The error.    NO values

Missing keys and custom error message with values
    [Documentation]    FAIL
    ...    The error.
    ...    Following keys missing from first dictionary: 'c'
    Dictionaries Should Be Equal    ${D2}    ${D3}    The error.

Different values
    [Documentation]    FAIL
    ...    Following keys have different values:
    ...    Key a: x != b
    ...    Key c: 3 (integer) != 3 (string)
    Dictionaries Should Be Equal    ${D3}    ${D3B}

Different values and custom error message
    [Documentation]    FAIL    The error.
    Dictionaries Should Be Equal    ${D3}    ${D3B}    The error.    False

Different values and custom error message with values
    [Documentation]    FAIL
    ...    The error.
    ...    Following keys have different values:
    ...    Key a: x != b
    ...    Key c: 3 (integer) != 3 (string)
    Dictionaries Should Be Equal    ${D3}    ${D3B}    The error.    values=yes

`ignore_keys`
    Dictionaries Should Be Equal    ${D2}    ${D3}     ignore_keys=${{['c']}}
    Dictionaries Should Be Equal    ${D3}    ${D3B}    ignore_keys=('c', 'a')

`ignore_keys` with non-string keys
    Dictionaries Should Be Equal    ${{{1: 2, (3, 4): 5, 'a': 'x'}}}    ${D1}    ignore_keys=[1, (3, 4)]

`ignore_keys` recursive
    Dictionaries Should Be Equal    ${{{1: {2: {3: {0: -3, 4: 5}, 0: -2}, 0: -1}}}}
    ...                             ${{{1: {2: {3: {4: 5}}}}}}    ignore_keys=[0]

`ignore_keys` with missing keys
    [Documentation]    FAIL    Following keys missing from second dictionary: 'c'
    Dictionaries Should Be Equal    ${D3}    ${D1}    ignore_keys=['b']

`ignore_keys` with wrong values
    [Documentation]    FAIL    Following keys have different values:
    ...    Key a: x != b
    Dictionaries Should Be Equal    ${D3}    ${D3B}    ignore_keys=['c']

`ignore_keys` as string must be valid expression
    [Documentation]    FAIL     ValueError: 'ignore_keys' value 'b' cannot be converted to a list.
    Dictionaries Should Be Equal    ${D3}    ${D1}    ignore_keys=b

`ignore_keys` must be list
    [Documentation]    FAIL     ValueError: 'ignore_keys' value '42' cannot be converted to a list.
    Dictionaries Should Be Equal    ${D3}    ${D1}    ignore_keys=42

`ignore_case`
    [Template]    Dictionaries Should Be Equal
    FOR    ${d}    IN    @{DICTS}
        ${d}    ${d}    ignore_case=True
        ${d}    ${d}    ignore_case=value
        ${d}    ${d}    ignore_case=key
    END
    ${D3}    ${D3C}    ignore_case=${True}
    ${DX}    ${{{'a': 'x', 'b': 'y', 'C': 3, 4: 'e', 'ss': 'strasse', 'list': ['A', 'B'], ('a', 'b'): 'tuple', 'dict': {'A': 'X', 'B': 'Y'}}}}
    ...                ignore_case=yes!

`ignore_case` with ´ignore_keys`
    [Documentation]    FAIL
    ...    Following keys missing from first dictionary: 'C'
    ...    Following keys missing from second dictionary: 'a'
    [Template]    Dictionaries Should Be Equal
    ${D3B}    ${D3C}    ignore_case=True       ignore_keys=['A', 'c']
    ${D3}     ${D3C}    ignore_case=${True}    ignore_keys=['A']
    ${D3}     ${D3C}    ignore_case=keys       ignore_keys=['a', 'B']
    ${D3B}    ${D3C}    ignore_case=value      ignore_keys=['a', 'A', 'c', 'C']
    ${D3B}    ${D3C}    ignore_case=values     ignore_keys=['A', 'c']
    ${DX}     ${{{'a': 'x', 'list': ['A', 'B'], 'dict': {'A': 'X'}}}}
    ...                 ignore_case=both       ignore_keys=['B', 'c', 4, 'ss', ('A', 'B')]

`ignore_case` when normalized keys have conflict
    [Documentation]    FAIL
    ...    Dictionary {'a': 1, 'A': 2} contains multiple keys that are normalized to 'a'. \
    ...    Try normalizing only dictionary values like 'ignore_case=values'.
    Dictionaries Should Be Equal    ${{{'a': 1, 'A': 2}}}    ${{{'a': 2, 'A': 1}}}    ignore_case=True
