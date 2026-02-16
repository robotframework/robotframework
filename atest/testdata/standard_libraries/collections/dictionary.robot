*** Settings ***
Test Setup        Create Dictionaries For Testing
Library           Collections
Library           CollectionsHelperLibrary.py

*** Variables ***
${IMMUTABLE}      ${{type('Immutable', (collections.abc.Mapping,), {'__getitem__': lambda s, k: {'a': 1, 'b': 2}[k], '__iter__': lambda s: iter(['a', 'b']), '__len__': lambda s: 2})()}}

*** Test Cases ***
Convert To Dictionary with mappings
    ${dotted} =    Create Dictionary    a=1    b=2
    Should Be True    type($dotted) is not dict
    ${normal} =    Convert To Dictionary    ${dotted}
    Should Be True    type($normal) is dict
    Should Be Equal    ${dotted}    ${normal}
    ${normal} =    Convert To Dictionary    ${IMMUTABLE}
    Should Be Equal    ${normal}    {'a': 1, 'b': 2}    type=dict

Convert To Dictionary with list of tuples
    ${from_empty_list} =    Convert To Dictionary    ${{()}}
    Should Be Equal    ${from_empty_list}    ${D0}
    ${from_tuple_list} =    Convert To Dictionary    ${{[('a', 1), ('b', 2)]}}
    Should Be Equal    ${from_tuple_list}    ${D2}

Set To Dictionary
    Set To Dictionary    ${D0}    a    ${1}
    Should Be Equal    ${D0}    ${D1}
    Set To Dictionary    ${D0}    b    ${2}    ${3}    ${None}
    Should Be Equal    ${D0}    ${D3}

Set To Dictionary With wrong number of arguments
    [Documentation]    FAIL ValueError: Adding data to a dictionary failed. There should be even number of key-value-pairs.
    Set To Dictionary    ${D0}    a

Set To Dictionary With **kwargs
    Set To Dictionary    ${D0}    k1    ${1}    over    write    k2=${2}    over=written
    Should Be Equal    ${D0}    {'k1': 1, 'k2': 2, 'over': 'written'}    type=dict

Set To Dictionary with immutable
    ${x} =    Set To Dictionary    ${IMMUTABLE}    b    ${2}
    ${y} =    Set To Dictionary    ${IMMUTABLE}    a    replace    c=new
    Should Be Equal    ${x}            {'a': 1, 'b': 2}                        type=dict
    Should Be Equal    ${y}            {'a': 'replace', 'b': 2, 'c': 'new'}    type=dict
    Should Be Equal    ${IMMUTABLE}    {'a': 1, 'b': 2}                        type=Mapping

Remove From Dictionary
    Remove From Dictionary    ${D3}    b    x    ${2}
    Should Be Equal    ${D3}    {'a': 1, 3: None}    type=dict
    Remove From Dictionary    ${D3}    ${TUPLE}
    Should Be Equal    ${D3}    {'a': 1, 3: None}    type=dict

Remove From Dictionary with immutable
    ${x} =    Remove From Dictionary    ${IMMUTABLE}    b
    ${y} =    Remove From Dictionary    ${IMMUTABLE}    a    b    c    d
    Should Be Equal    ${x}            {'a': 1}            type=dict
    Should Be Equal    ${y}            {}                  type=dict
    Should Be Equal    ${IMMUTABLE}    {'a': 1, 'b': 2}    type=Mapping

Keep In Dictionary
    Keep In Dictionary    ${D3}    a    x    ${2}    ${3}
    Should Be Equal    ${D3}    {'a': 1, 3: None}    type=dict

Keep In Dictionary with immutable
    ${x} =    Keep In Dictionary    ${IMMUTABLE}    b
    ${y} =    Keep In Dictionary    ${IMMUTABLE}    a    b    c    d
    Should Be Equal    ${x}            {'b': 2}            type=dict
    Should Be Equal    ${y}            {'a': 1, 'b': 2}    type=dict
    Should Be Equal    ${IMMUTABLE}    {'a': 1, 'b': 2}    type=Mapping

Copy Dictionary
    ${copy} =    Copy Dictionary    ${D3}
    Remove From Dictionary    ${copy}    a    ${3}
    Should Be Equal    ${copy}    {'b': 2}                     type=dict
    Should Be Equal    ${D3}      {'a': 1, 'b': 2, 3: None}    type=dict

Shallow Copy Dictionary
    ${x2} =    Create Dictionary    x2    1
    ${a} =    Create Dictionary    x1    ${x2}
    ${b} =    Copy Dictionary    ${a}
    Set To Dictionary    ${a['x1']}    x2    2
    Should Be Equal    ${a['x1']['x2']}    2
    Should Be Equal    ${b['x1']['x2']}    2

Deep Copy Dictionary
    ${x2} =    Create Dictionary    x2    1
    ${a} =    Create Dictionary    x1    ${x2}
    ${b} =    Copy Dictionary    ${a}    deepcopy=True
    Set To Dictionary    ${a['x1']}    x2    2
    Set To Dictionary    ${b['x1']}    x2    3
    Should Be Equal    ${a['x1']['x2']}    2
    Should Be Equal    ${b['x1']['x2']}    3

Get Dictionary Keys Sorted
    ${keys} =    Get Dictionary Keys    ${D3B}
    Should Be Equal    ${keys}    ['a', 'b', 'c']    type=list

Get Dictionary Keys Unsorted
    ${keys} =    Get Dictionary Keys    ${D3B}    sort_keys=${False}
    Should Be Equal    ${keys}    ['b', 'a', 'c']    type=list

Get Dictionary Values Sorted
    ${values} =    Get Dictionary Values    ${D3B}
    Should Be Equal    ${values}    [1, 2, '']    type=list

Get Dictionary Values Unsorted
    ${values} =    Get Dictionary Values    ${D3B}    sort_keys=False
    Should Be Equal    ${values}    [2, 1, '']    type=list

Get Dictionary Items Sorted
    ${items} =    Get Dictionary Items    ${D3B}
    Should Be Equal    ${items}    ['a', 1, 'b', 2, 'c', '']    type=list

Get Dictionary Items Unsorted
    ${items} =    Get Dictionary Items    ${D3B}    sort_keys=NO
    Should Be Equal    ${items}    ['b', 2, 'a', 1, 'c', '']    type=list

Get Dictionary Keys/Values/Items When Keys Are Unorderable
    ${unorderable} =    Evaluate    {complex(1): 1, complex(2): 2, complex(3): 3}
    ${keys} =      Get Dictionary Keys      ${unorderable}
    ${values} =    Get Dictionary Values    ${unorderable}
    ${items} =     Get Dictionary Items     ${unorderable}
    Should Be Equal    ${keys}      ${{[complex(1), complex(2), complex(3)]}}
    Should Be Equal    ${values}    ${{[1, 2, 3]}}
    Should Be Equal    ${items}     ${{[complex(1), 1, complex(2), 2, complex(3), 3]}}

Get From Dictionary
    ${value} =    Get From Dictionary    ${D3}    b
    Should Be Equal As Integers    ${value}    2

Get From Dictionary With Invalid Key 1
    [Documentation]    FAIL Dictionary does not contain key 'x'.
    Get From Dictionary    ${D3}    x

Get From Dictionary With Invalid Key 2
    [Documentation]    FAIL Dictionary does not contain key '(1, 2)'.
    Get From Dictionary    ${D3}    ${TUPLE}

Get From Dictionary With Default
    ${dict} =    Create Dictionary    a=a    b=b
    ${value} =    Get From Dictionary    ${dict}    x     default_value
    Should Be Equal    ${value}    default_value
    ${value} =    Get From Dictionary    ${dict}    a     default_value
    Should Be Equal    ${value}    a

Log Dictionary With Different Log Levels
    Log Dictionary    ${D3B}
    Log Dictionary    ${D3B}    tRAce
    Log Dictionary    ${D3B}    warn
    Log Dictionary    ${D3B}    DEbug
    Log Dictionary    ${D3B}    INFO

Log Dictionary With Different Dictionaries
    Log Dictionary    ${D0}
    Log Dictionary    ${D1}
    ${dict} =    Evaluate    collections.OrderedDict(((True, 'xxx'), ('foo', []), ((1, 2, 3), 3.14)))
    Log Dictionary    ${dict}
    Log Dictionary    ${IMMUTABLE}

Pop From Dictionary Without Default
    [Documentation]   FAIL Dictionary does not contain key 'a'.
    ${dict} =    Create Dictionary    a=val    b=val2
    ${a} =    Pop From Dictionary    ${dict}    a
    Should Be Equal    ${a}    val
    Should Be Equal    ${dict}    {'b': 'val2'}    type=dict
    Pop From Dictionary    ${dict}    a

Pop From Dictionary With Default
    ${dict} =    Create Dictionary    a=val    b=val2
    ${a} =    Pop From Dictionary    ${dict}    a   foo
    Should Be Equal    ${a}    val
    Should Be Equal    ${dict}    {'b': 'val2'}    type=dict
    ${a} =    Pop From Dictionary    ${dict}    a   foo
    Should Be Equal    ${a}    foo
    Should Be Equal    ${dict}    {'b': 'val2'}    type=dict

Pop From Dictionary with immutable
    ${a} =    Pop From Dictionary    ${IMMUTABLE}    a
    Should Be Equal    ${a}    1    type=int
    Should Be Equal    ${IMMUTABLE}    {'a': 1, 'b': 2}    type=Mapping

Check invalid dictionary argument errors
    [Template]    Validate invalid argument error
    VAR    ${invalid_arg}    I'm not a dict, I'm string.
    Copy dictionary
    Dictionary Should Contain Item             ${invalid_arg}    a    b
    Dictionaries Should Be Equal               ${invalid_arg}    ${D2}    arg_name=dict1
    Dictionaries Should Be Equal               ${D2}    ${invalid_arg}    arg_name=dict2   invalid_argument=${invalid_arg}
    Dictionary Should Contain Key              ${invalid_arg}    a
    Dictionary Should Contain Sub Dictionary   ${invalid_arg}    ${D2}    arg_name=dict1
    Dictionary Should Contain Sub Dictionary   ${D2}    ${invalid_arg}    arg_name=dict2    invalid_argument=${invalid_arg}
    Dictionary Should Contain Value            ${invalid_arg}    a
    Dictionary Should Not Contain Key          ${invalid_arg}    a
    Dictionary Should Not Contain Value        ${invalid_arg}    a
    Get Dictionary Items
    Get Dictionary Keys
    Get Dictionary Values
    Get from dictionary                        ${invalid_arg}    a
    Keep in dictionary                         ${invalid_arg}    a
    Log Dictionary
    Pop From Dictionary                        ${invalid_arg}    a
    Remove From Dictionary                     ${invalid_arg}    a
    Set To Dictionary                          ${invalid_arg}    a    b

Bytes normalization
    Dictionary Should Contain Key             ${{{b'RF': 1}}}    ${{b'rf'}}      ignore_case=True

*** Keywords ***
Validate invalid argument error
    [Arguments]  ${keyword}    ${argument}=I'm not a dict, I'm a string.    @{args}    ${arg_name}=dictionary    ${annotation}=Mapping    ${invalid_argument}=${NONE}
    IF    not $invalid_argument
        VAR    ${invalid_argument}    ${argument}
    END
    Run keyword and expect error
    ...    ValueError: Argument '${arg_name}' got value '${invalid_argument}' that cannot be converted to ${annotation}: Invalid expression.
    ...    ${keyword}    ${argument}    @{args}

Create Dictionaries For Testing
    ${D0}    Create Dictionary
    Set Test Variable    \${D0}
    ${D1} =    Create Dictionary    a=${1}
    Set Test Variable    \${D1}
    ${D2} =    Create Dictionary    a=${1}    b=${2}
    Set Test Variable    \${D2}
    ${D2B} =    Create Dictionary    a=1    b=x
    Set Test Variable    \${D2B}
    ${D3}    Create Dictionary    a=${1}    b=${2}    ${3}=${None}
    Set Test Variable    \${D3}
    ${D3B}    Create Dictionary    b=${2}    a=${1}    c=
    Set Test Variable    \${D3B}
    ${BIG} =    Evaluate    {'a': 1, 'B': 2, 3: [42], 'd': '', '': 'e', (): {}}
    Set Test Variable    \${BIG}
    ${TUPLE} =    Evaluate    (1, 2)
    Set Test Variable    \${TUPLE}
    ${D4} =    Create Dictionary    a=1    b=2    c=3    d=4    e=5
    Set Test Variable    \${D4}
    ${D4B} =    Create Dictionary    d=4    b=2    e=5    a=1    c=3
    Set Test Variable    \${D4B}
