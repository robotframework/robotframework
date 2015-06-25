*** Settings ***
Test Setup        Create Dictionaries For Testing
Resource          collections_resources.robot
Library           CollectionsHelperLibrary.py

*** Test Cases ***
Convert To Dictionary
    ${dotted} =    Create Dictionary    a=1    b=2
    Should Be True    type(dotted) is not dict
    ${normal} =    Convert To Dictionary    ${dotted}
    Should Be True    type(normal) is dict
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

Keep In Dictionary
    Keep In Dictionary    ${D3}    a    x    ${2}    ${3}
    Compare To Expected String    ${D3}    {'a': 1, 3: None}

Copy Dictionary
    ${copy} =    Copy Dictionary    ${D3}
    Remove From Dictionary    ${copy}    a    ${3}
    Compare To Expected String    ${copy}    {'b':2}
    Compare To Expected String    ${D3}    {'a': 1, 'b': 2, 3: None}

Get Dictionary Keys
    ${keys} =    Get Dictionary Keys    ${D3}
    Compare To Expected String    ${keys}    [3, 'a', 'b']
    ${keys} =    Get Dictionary Keys    ${BIG}
    Compare To Expected String    ${keys}    [3, '', 'B', 'a', 'd', ()]

Get Dictionary Values
    ${values} =    Get Dictionary Values    ${D3}
    Compare To Expected String    ${values}    [None, 1, 2]
    ${values} =    Get Dictionary Values    ${BIG}
    Compare To Expected String    ${values}    [[42], 'e', 2, 1, '', {}]

Get Dictionary Items
    ${items} =    Get Dictionary Items    ${D3}
    Compare To Expected String    ${items}    [3, None, 'a', 1, 'b', 2]
    ${items} =    Get Dictionary Items    ${BIG}
    Compare To Expected String    ${items}    [3, [42], '', 'e', 'B', 2, 'a', 1, 'd', '', (), {}]

Get From Dictionary
    ${value} =    Get From Dictionary    ${D3}    b
    Should Be Equal As Integers    ${value}    2

Get From Dictionary With Invalid Key
    [Documentation]    FAIL Dictionary does not contain key 'x'.
    Get From Dictionary    ${D3}    x

Dictionary Should Contain Key
    Dictionary Should Contain Key    ${D3}    a

Dictionary Should Contain Key With Missing Key
    [Documentation]    FAIL Dictionary does not contain key 'x'.
    Dictionary Should Contain Key    ${D3}    x

Dictionary Should Contain Item
    Dictionary Should Contain Item    ${D3}    a    1

Dictionary Should Contain Item With Missing Key
    [Documentation]    FAIL Dictionary does not contain key 'x'.
    Dictionary Should Contain Item    ${D3}    x    1

Dictionary Should Contain Item With Wrong Value
    [Documentation]    FAIL Value of dictionary key 'a' does not match: 1 != 2
    Dictionary Should Contain Item    ${D3}    a    2

Dictionary Should Not Contain Key
    Dictionary Should Not Contain Key    ${D3}    x

Dictionary Should Not Contain Key With Existing Key
    [Documentation]    FAIL Dictionary contains key 'b'.
    Dictionary Should Not Contain Key    ${D3}    b

Dictionary Should (Not) Contain Key Does Not Require `has_key`
    ${dict} =    Get Dict Without Has Key    name=value
    Dictionary Should Contain Key    ${dict}    name
    Dictionary Should Not Contain Key    ${dict}    nonex

Dictionary Should Contain Value
    Dictionary Should Contain Value    ${D3}    ${2}

Dictionary Should Contain Value With Missing Value
    [Documentation]    FAIL Dictionary does not contain value 'x'.
    Dictionary Should Contain Value    ${D3}    x

Dictionary Should Not Contain Value
    Dictionary Should Not Contain Value    ${D3}    x

Dictionary Should Not Contain Value With Existing Value
    [Documentation]    FAIL Dictionary contains value '2'.
    Dictionary Should Not Contain Value    ${D3}    ${2}

Dictionaries Should Be Equal
    Dictionaries Should Be Equal    ${D0}    ${D0}
    Dictionaries Should Be Equal    ${D3}    ${D3}
    Dictionaries Should Be Equal    ${BIG}    ${BIG}

Dictionaries Should Equal With First Dictionary Missing Keys
    [Documentation]    FAIL Following keys missing from first dictionary: 3
    Dictionaries Should Be Equal    ${D2}    ${D3}

Dictionaries Should Equal With Second Dictionary Missing Keys
    [Documentation]    FAIL Following keys missing from second dictionary: a, b
    Dictionaries Should Be Equal    ${D2}    ${D0}

Dictionaries Should Equal With Both Dictionaries Missing Keys
    [Documentation]    FAIL
    ...    Following keys missing from first dictionary: b
    ...    Following keys missing from second dictionary: , B, d, ()
    Dictionaries Should Be Equal    ${BIG}    ${D3}

Dictionaries Should Be Equal With Different Keys And Own Error Message
    [Documentation]    FAIL My error message!
    Dictionaries Should Be Equal    ${D2}    ${D3}    My error message!    NO values

Dictionaries Should Be Equal With Different Keys And Own And Default Error Messages
    [Documentation]    FAIL
    ...    My error message!
    ...    Following keys missing from first dictionary: 3
    Dictionaries Should Be Equal    ${D2}    ${D3}    My error message!    values=yes

Dictionaries Should Be Equal With Different Values
    [Documentation]    FAIL
    ...    Following keys have different values:
    ...    Key a: 1 (integer) != 1 (string)
    ...    Key b: 2 != x
    Dictionaries Should Be Equal    ${D2}    ${D2B}

Dictionaries Should Be Equal With Different Values And Own Error Message
    [Documentation]    FAIL My error message!
    Dictionaries Should Be Equal    ${D2}    ${D2B}    My error message!    False

Dictionaries Should Be Equal With Different Values And Own And Default Error Messages
    [Documentation]    FAIL
    ...    My error message!
    ...    Following keys have different values:
    ...    Key a: 1 (integer) != 1 (string)
    ...    Key b: 2 != x
    Dictionaries Should Be Equal    ${D2}    ${D2B}    My error message!

Dictionary Should Contain Sub Dictionary
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D2}
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D0}

Dictionary Should Contain Sub Dictionary With Missing Keys
    [Documentation]    FAIL Following keys missing from first dictionary: 3
    Dictionary Should Contain Sub Dictionary    ${D2}    ${D3}

Dictionary Should Contain Sub Dictionary With Missing Keys And Own Error Message
    [Documentation]    FAIL My error message!
    Dictionary Should Contain Sub Dictionary    ${D2}    ${D3}    My error message!    False

Dictionary Should Contain Sub Dictionary With Missing Keys And Own And Default Error Message
    [Documentation]    FAIL
    ...    My error message!
    ...    Following keys missing from first dictionary: 3
    Dictionary Should Contain Sub Dictionary    ${D2}    ${D3}    My error message!

Dictionary Should Contain Sub Dictionary With Different Value
    [Documentation]    FAIL
    ...    Following keys have different values:
    ...    Key a: 1 (integer) != 1 (string)
    ...    Key b: 2 != x
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D2B}

Dictionary Should Contain Sub Dictionary With Different Value And Own Error Message
    [Documentation]    FAIL My error message!
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D2B}    My error message!    False

Dictionary Should Contain Sub Dictionary With Different Value And Own And Default Error Message
    [Documentation]    FAIL
    ...    My error message!
    ...    Following keys have different values:
    ...    Key a: 1 (integer) != 1 (string)
    ...    Key b: 2 != x
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D2B}    My error message!

Log Dictionary With Different Log Levels
    Log Dictionary    ${D3}
    Log Dictionary    ${D3}    tRAce
    Log Dictionary    ${D3}    warn
    Log Dictionary    ${D3}    DEbug
    Log Dictionary    ${D3}    INFO

Log Dictionary With Different Dictionaries
    Log Dictionary    ${D0}
    Log Dictionary    ${D1}
    ${dict} =    Evaluate    {(1, 2, 3): 3.14, True: 'xxx', 'foo': []}
    Log Dictionary    ${dict}

*** Keywords ***
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
    ${BIG} =    Evaluate    {'a': 1, 'B': 2, 3: [42], 'd': '', '': 'e', (): {}}
    Set Test Variable    \${BIG}
