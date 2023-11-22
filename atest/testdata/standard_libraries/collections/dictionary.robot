*** Settings ***
Test Setup        Create Dictionaries For Testing
Resource          collections_resources.robot
Library           CollectionsHelperLibrary.py

*** Test Cases ***
Convert To Dictionary
    ${dotted} =    Create Dictionary    a=1    b=2
    Should Be True    type($dotted) is not dict
    ${normal} =    Convert To Dictionary    ${dotted}
    Should Be True    type($normal) is dict
    Should Be Equal    ${dotted}    ${normal}

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
    Compare To Expected String    ${D0}    {'k1': 1, 'k2': 2, 'over': 'written'}

Remove From Dictionary
    Remove From Dictionary    ${D3}    b    x    ${2}
    Compare To Expected String    ${D3}    {'a': 1, 3: None}
    Remove From Dictionary    ${D3}    ${TUPLE}
    Compare To Expected String    ${D3}    {'a': 1, 3: None}

Keep In Dictionary
    Keep In Dictionary    ${D3}    a    x    ${2}    ${3}
    Compare To Expected String    ${D3}    {'a': 1, 3: None}

Copy Dictionary
    ${copy} =    Copy Dictionary    ${D3}
    Remove From Dictionary    ${copy}    a    ${3}
    Compare To Expected String    ${copy}    {'b':2}
    Compare To Expected String    ${D3}    {'a': 1, 'b': 2, 3: None}

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
    Compare To Expected String    ${keys}    ['a', 'b', 'c']

Get Dictionary Keys Unsorted
    ${keys} =    Get Dictionary Keys    ${D3B}    sort_keys=${False}
    Compare To Expected String    ${keys}    ['b', 'a', 'c']

Get Dictionary Values Sorted
    ${values} =    Get Dictionary Values    ${D3B}
    Compare To Expected String    ${values}    [1, 2, '']

Get Dictionary Values Unsorted
    ${values} =    Get Dictionary Values    ${D3B}  sort_keys=False
    Compare To Expected String    ${values}    [2, 1, '']

Get Dictionary Items Sorted
    ${items} =    Get Dictionary Items    ${D3B}
    Compare To Expected String    ${items}    ['a', 1, 'b', 2, 'c', '']

Get Dictionary Items Unsorted
    ${items} =    Get Dictionary Items    ${D3B}    sort_keys=NO
    Compare To Expected String    ${items}    ['b', 2, 'a', 1, 'c', '']

Get Dictionary Keys/Values/Items When Keys Are Unorderable
    ${unorderable} =    Evaluate    {complex(1): 1, complex(2): 2, complex(3): 3}
    ${keys} =    Get Dictionary Keys    ${unorderable}
    Compare To Expected String    ${keys}    list(d)    d=${unorderable}
    ${values} =    Get Dictionary Values    ${unorderable}
    Compare To Expected String    ${values}    list(d.values())    d=${unorderable}
    ${items} =    Get Dictionary Items    ${unorderable}
    Compare To Expected String    ${items}    [i for item in d.items() for i in item]    d=${unorderable}

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
    ${dict} =    Evaluate    collections.OrderedDict(((True, 'xxx'), ('foo', []), ((1, 2, 3), 3.14)))   modules=collections
    Log Dictionary    ${dict}

Pop From Dictionary Without Default
    [Documentation]   FAIL Dictionary does not contain key 'a'.
    ${dict} =    Create Dictionary    a=val    b=val2
    ${a} =    Pop From Dictionary    ${dict}    a
    Should be equal    ${a}    val
    Should be True   $dict == {'b': 'val2'}
    Pop From Dictionary    ${dict}    a

Pop From Dictionary With Default
    ${dict} =    Create Dictionary    a=val    b=val2
    ${a} =    Pop From Dictionary    ${dict}    a   foo
    Should be equal    ${a}    val
    Should be True   $dict == {'b': 'val2'}
    ${a} =    Pop From Dictionary    ${dict}    a   foo
    Should be equal    ${a}    foo
    Should be True   $dict == {'b': 'val2'}

Check invalid dictionary argument errors
    [Template]    Validate invalid argument error
    Copy dictionary
    Dictionary Should Contain Item             I'm not a dict, I'm string.    a    b
    Dictionaries Should Be Equal               I'm not a dict, I'm string.    ${D2}
    Dictionaries Should Be Equal               ${D2}    I'm not a dict, I'm string.    position=2
    Dictionary Should Contain Key              I'm not a dict, I'm string.    a
    Dictionary Should Contain Sub Dictionary   I'm not a dict, I'm string.    ${D2}
    Dictionary Should Contain Sub Dictionary   ${D2}    I'm not a dict, I'm string.    position=2
    Dictionary Should Contain Value            I'm not a dict, I'm string.    a
    Dictionary Should Not Contain Key          I'm not a dict, I'm string.    a
    Dictionary Should Not Contain Value        I'm not a dict, I'm string.    a
    Get Dictionary Items
    Get Dictionary Keys
    Get Dictionary Values
    Get from dictionary                        I'm not a dict, I'm string.    a
    Keep in dictionary                         I'm not a dict, I'm string.    a
    Log Dictionary
    Pop From Dictionary                        I'm not a dict, I'm string.    a
    Remove From Dictionary                     I'm not a dict, I'm string.    a
    Set To Dictionary                          I'm not a dict, I'm string.    a    b

*** Keywords ***
Validate invalid argument error
    [Arguments]  ${keyword}    ${argument}=I'm not a dict, I'm a string.    @{args}    ${type}=string    ${position}=1
    Run keyword and expect error
    ...    TypeError: Expected argument ${position} to be a dictionary, got ${type} instead.
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
