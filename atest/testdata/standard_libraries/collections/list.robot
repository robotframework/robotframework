*** Settings ***
Test Setup        Create Lists for the Tests
Resource          collections_resources.robot

*** Variables ***
${INDEX ERROR}          ValueError: Cannot convert index 'index' to an integer.
${LIST OUT OF RANGE}    IndexError: Given index 10 is out of the range 0-2.

*** Test Cases ***
Convert To List
    ${string list} =    Convert To List    hello
    Compare To Expected String    ${string list}    [ 'h', 'e', 'l', 'l', 'o' ]
    ${tuple} =    Evaluate    (1, 2, 3)
    ${tuple list} =    Convert To List    ${tuple}
    Compare To Expected String    ${tuple list}    [ 1, 2, 3 ]

Convert To List With Invalid Type
    [Documentation]    FAIL STARTS: TypeError:
    Convert To List    ${1}

Append To List
    Append To List    ${L0}    1
    Compare To Expected String    ${L0}    ['1']
    Append To List    ${L0}    2    3    4
    Compare To Expected String    ${L0}    [ '1', '2', '3', '4' ]

Insert Into List With String Index
    Insert Into List And Compare    ${L2}    1    value    ['1', 'value', 2]

Insert Into List With Int Index
    Insert Into List And Compare    ${L2}    ${1}    value    ['1', 'value', 2]

Insert Into List With Index Over Lists Size
    Insert Into List And Compare    ${L2}    1000    value    ['1', 2, 'value']

Insert Into List With Index Negative Index
    Insert Into List And Compare    ${L4}    -2    value    ['41', 42, 'value', '43' ,'44']

Insert Into List With Index Under Lists Size
    Insert Into List And Compare    ${L2}    -1000    value    ['value' , '1', 2]

Insert Into List With Invalid Index
    [Documentation]    FAIL ${INDEX ERROR}
    Insert Into List    ${L3}    index    value

Combine Lists
    ${combined list} =    Combine Lists    ${L1}    ${L2}
    Compare To Expected String    ${combined list}    ['1', '1', 2]
    ${combined list} =    Combine Lists    ${L1}    ${L2}    ${L3}    ${L0}
    Compare To Expected String    ${combined list}    ['1', '1', 2, '11', 12, '13']

Set List Value
    Set List Value    ${L3}    1    value
    Compare To Expected String    ${L3}    ['11', 'value', '13']

Set List Value Index Out Of List
    [Documentation]    FAIL ${LIST OUT OF RANGE}
    Set List Value    ${L3}    10    value

Set List Value With Invalid Index
    [Documentation]    FAIL ${INDEX ERROR}
    Set List Value    ${L3}    index    value

Remove Values From List
    Remove Values From List    ${LONG}    ${42}
    Compare To Expected String    ${LONG}    [ '1', '1', 2, '41', '43', '44', '1', 2]
    Remove Values From List    ${LONG}    ${2}    ${42}    1
    Compare To Expected String    ${LONG}    [ '41', '43', '44' ]

Remove Non Existing Values From List
    Remove Values From List    ${L3}    1234
    Compare To Expected String    ${L3}    [ '11', 12, '13' ]

Remove From List
    ${removed value} =    Remove From List    ${L3}    1
    Should Be Equal    ${removed value}    ${12}
    Compare To Expected String    ${L3}    [ '11', '13' ]
    ${removed value} =    Remove From List    ${L3}    -2
    Should Be Equal    ${removed value}    11
    Compare To Expected String    ${L3}    [ '13' ]

Remove From List Index Out Of List
    [Documentation]    FAIL ${LIST OUT OF RANGE}
    Remove From List    ${L3}    10

Remove From List With Invalid Index
    [Documentation]    FAIL ${INDEX ERROR}
    Remove From List    ${L3}    index

Remove Duplicates
    ${result} =    Remove Duplicates    ${L3}
    Should Be Equal    ${result}    ${L3}
    ${result} =    Remove Duplicates    ${LONG}
    Compare To Expected String    ${result}    ['1', 2, '41', 42, '43', '44']

Count Values In List
    ${count} =    Count Values In List    ${LONG}    1
    Should Be Equal As Integers    ${count}    3
    ${count} =    Count Values In List    ${LONG}    ${2}
    Should Be Equal As Integers    ${count}    2
    ${count} =    Count Values In List    ${LONG}    1    3
    Should Be Equal As Integers    ${count}    1
    ${count} =    Count Values In List    ${LONG}    1    0    4
    Should Be Equal As Integers    ${count}    2

Count Values In List With Invalid Start Index
    [Documentation]    FAIL ${INDEX ERROR}
    Count Values In List    ${LONG}    2    index    1

Count Values In List With Invalid Stop Index
    [Documentation]    FAIL ${INDEX ERROR}
    Count Values In List    ${LONG}    2    1    index

Get Index From List
    ${position} =    Get Index From List    ${LONG}    ${2}
    Should Be Equal As Integers    ${position}    2
    ${position} =    Get Index From List    ${LONG}    ${2}    3
    Should Be Equal As Integers    ${position}    8
    ${position} =    Get Index From List    ${LONG}    43    4    7
    Should Be Equal As Integers    ${position}    5
    ${position} =    Get Index From List    ${LONG}    43    ${EMPTY}    8
    Should Be Equal As Integers    ${position}    5

Get Index From List With Non Existing Value
    ${position} =    Get Index From List    ${LONG}    1234
    Should Be Equal As Integers    ${position}    -1

Get Index From List With Invalid Start Index
    [Documentation]    FAIL ${INDEX ERROR}
    Get Index From List    ${LONG}    2    index    1

Get Index From List With Invalid Stop Index
    [Documentation]    FAIL ${INDEX ERROR}
    Get Index From List    ${LONG}    2    1    index

Copy List
    ${copy} =    Copy List    ${L2}
    Append To List    ${L2}    1    2    3
    Compare To Expected String    ${copy}    ['1', 2]

Reserve List
    Reverse List    ${LONG}
    Compare To Expected String    ${LONG}    [2, '1', '44', '43', 42, '41', 2, '1', '1']

Sort List
    Sort List    ${LONG}
    Compare To Expected String    ${LONG}    [ 2, 2, 42, '1', '1' , '1', '41', '43', '44']

Get From List
    ${value} =    Get From List    ${L4}    1
    Should Be Equal As Integers    ${value}    42
    ${value} =    Get From List    ${L4}    -2
    Should Be Equal As Integers    ${value}    43

Get From List With Invalid Index
    [Documentation]    FAIL ${INDEX ERROR}
    Get From List    ${L3}    index

Get From List Out Of List Index
    [Documentation]    FAIL ${LIST OUT OF RANGE}
    Get From List    ${L3}    10

Get Slice From List
    ${values} =    Get Slice From List    ${L4}    1    2
    Compare To Expected String    ${values}    [42]
    ${values} =    Get Slice From List    ${L4}    1
    Compare To Expected String    ${values}    [42, '43', '44']
    ${values} =    Get Slice From List    ${L4}    ${EMPTY}    2
    Compare To Expected String    ${values}    ['41', 42]
    ${values} =    Get Slice From List    ${L4}
    Should Be Equal    ${values}    ${L4}

Get Slice From List With Invalid Start Index
    [Documentation]    FAIL ${INDEX ERROR}
    Get Slice From List    ${L4}    index    2

Get Slice From List With Invalid Stop Index
    [Documentation]    FAIL ${INDEX ERROR}
    Get Slice From List    ${L4}    2    index

Get Slice From List With Out Of List Index
    ${values} =    Get Slice From List    ${L3}    10    10
    Should Be Equal    ${values}    ${L0}

List Should Contain Value
    List Should Contain Value    ${L1}    1

List Should Contain Value, Value Not Found
    [Documentation]    FAIL [ 1 ] does not contain value '2'.
    List Should Contain Value    ${L1}    2

List Should Contain Value, Value Not Found And Own Error Message
    [Documentation]    FAIL My error message!
    List Should Contain Value    ${L1}    2    My error message!

List Should Not Contain Value
    List Should Not Contain Value    ${L1}    2

List Should Not Contain Value, Value Found
    [Documentation]    FAIL [ 1 ] contains value '1'.
    List Should Not Contain Value    ${L1}    1

List Should Not Contain Value, Value Found And Own Error Message
    [Documentation]    FAIL My error message!
    List Should Not Contain Value    ${L1}    1    My error message!

List Should Not Contain Duplicates With No Duplicates
    ${iterable}    ${tuple} =    Evaluate    xrange(100), (0, 1, 2, '0', '1', '2')
    : FOR    ${list}    IN    ${L0}    ${L1}    ${L2}    ${L3}
    ...    ${L4}    ${iterable}    ${tuple}
    \    List Should Not Contain Duplicates    ${list}

List Should Not Contain Duplicates Is Case And Space Sensitive
    ${list} =    Create List    item    ITEM    i tem    i t e m    ITE_m
    List Should Not Contain Duplicates    ${list}

List Should Not Contain Duplicates With One Duplicate
    [Documentation]    FAIL 'item' found multiple times.
    ${list} =    Create List    item    item    another item    fourth item    ITEM
    List Should Not Contain Duplicates    ${list}

List Should Not Contain Duplicates With Multiple Duplicates
    [Documentation]    FAIL '2', 'None', '4', '[1, 2, 3]' and '[]' found multiple times.
    ${list} =    Evaluate    [1, 2, '2', 2, None, '4', '4', '4', '4', '42', [1, 2, 3], {}, False] + [[]]*10 + [[1, 2, 3], None, (1, 2, 3, 4), 'a', 'A']
    List Should Not Contain Duplicates    ${list}

List Should Not Contain Duplicates With Custom Error Message
    [Documentation]    FAIL My special error
    List Should Not Contain Duplicates    ${L0}    This would be the error but this time the keyword passes
    ${list} =    Evaluate    (42,) * 42
    List Should Not Contain Duplicates    ${list}    My special error

Lists Should Be Equal
    Lists Should Be Equal    ${L4}    ${L4}
    Lists Should Be Equal    ${L2}    ${L2}
    Lists Should Be Equal    ${L0}    ${L0}

Lists Should Be Equal With Different Lengths
    [Documentation]    FAIL Lengths are different: 1 != 4
    Lists Should Be Equal    ${L1}    ${L4}

Lists Should Be Equal With Different Lengths And Own Error Message
    [Documentation]    FAIL My error message!
    Lists Should Be Equal    ${L1}    ${L4}    My error message!    False

Lists Should Be Equal With Different Lengths And Own And Default Error Messages
    [Documentation]    FAIL My error message!
    ...    Lengths are different: 1 != 4
    Lists Should Be Equal    ${L1}    ${L4}    My error message!

Lists Should Be Equal With Different Values
    [Documentation]    FAIL Lists are different:
    ...    Index 0: 11 != 10
    ...    Index 1: 12 (integer) != 12 (string)
    ...    Index 2: 13 != 14
    Lists Should Be Equal    ${L3}    ${L3B}

Lists Should Be Equal With Different Values And Own Error Message
    [Documentation]    FAIL My error message!
    Lists Should Be Equal    ${L3}    ${L3B}    My error message!    False

Lists Should Be Equal With Different Values And Own And Default Error Messages
    [Documentation]    FAIL My error message!
    ...    Lists are different:
    ...    Index 0: 11 != 10
    ...    Index 1: 12 (integer) != 12 (string)
    ...    Index 2: 13 != 14
    Lists Should Be Equal    ${L3}    ${L3B}    My error message!

Lists Should Be Equal With Named Indices As List
    [Documentation]    FAIL Lists are different:
    ...    Index 0 (a): 11 != 10
    ...    Index 1 (b): 12 (integer) != 12 (string)
    ...    Index 2 (c): 13 != 14
    ${names} =    Create List    a    b    c    ignored
    Lists Should Be Equal    ${L3}    ${L3B}    names=${names}

Lists Should Be Equal With Named Indices As List With Too Few Values
    [Documentation]    FAIL My message
    ...    Lists are different:
    ...    Index 0 (a): 11 != 10
    ...    Index 1 (b): 12 (integer) != 12 (string)
    ...    Index 2: 13 != 14
    ${names} =    Create List    a    b
    Lists Should Be Equal    ${L3}    ${L3B}    My message    names=${names}

Lists Should Be Equal With Named Indices As Dictionary
    [Documentation]    FAIL Lists are different:
    ...    Index 0 (a): 11 != 10
    ...    Index 1 (b): 12 (integer) != 12 (string)
    ...    Index 2 (c): 13 != 14
    ${names} =    Create Dictionary    0=a    1=b    2=c    42=ignored
    Lists Should Be Equal    ${L3}    ${L3B}    names=${names}

Lists Should Be Equal With Named Indices As Dictionary With Too Few Values
    [Documentation]    FAIL Lists are different:
    ...    Index 0 (a): 11 != 10
    ...    Index 1: 12 (integer) != 12 (string)
    ...    Index 2 (c): 13 != 14
    ${names} =    Create Dictionary    0=a    2=c
    Lists Should Be Equal    ${L3}    ${L3B}    names=${names}

List Should Contain Sub List
    List Should Contain Sub List    ${LONG}    ${L4}

List Should Contain Sub List With Missing Values
    [Documentation]    FAIL Following values were not found from first list: 1, 1, 2, 1, 2
    List Should Contain Sub List    ${L4}    ${LONG}

List Should Contain Sub List With Missing Values And Own Error Message
    [Documentation]    FAIL My error message!
    List Should Contain Sub List    ${L4}    ${LONG}    My error message!    No Values

List Should Contain Sub List With Missing Values And Own And Default Error Messages
    [Documentation]    FAIL My error message!
    ...    Following values were not found from first list: 1, 1, 2, 1, 2
    List Should Contain Sub List    ${L4}    ${LONG}    My error message!    values=please

Log List With Different Log Levels
    Log List    ${L3}
    Log List    ${L3}    tRAce
    Log List    ${L3}    warn
    Log List    ${L3}    DEbug
    Log List    ${L3}    INFO

Log List With Different Lists
    Log List    ${L0}
    Log List    ${L1}
    ${tuple} =    Evaluate    (1, 2, 3)
    ${list} =    Create List    ${tuple}    ${3.12}
    Log List    ${list}

Count Matches In List Case Insensitive
    [Template]    Match Count Should Be
    1    ${STRINGS}    a
    0    ${STRINGS}    A
    1    ${STRINGS}    A       case_insensitive=True
    2    ${STRINGS}    word    case_insensitive=True
    2    ${STRINGS}    b       case_insensitive=True
    1    ${STRINGS}    b

Count Matches In List Whitespace Insensitive
    [Template]    Match Count Should Be
    4    ${WHITESPACE_STRINGS}    word     whitespace_insensitive=True    case_insensitive=True
    3    ${WHITESPACE_STRINGS}    word     whitespace_insensitive=yes
    0    ${WHITESPACE_STRINGS}    words    whitespace_insensitive=${1}    case_insensitive=${2}

Count Matches In List Regexp
    [Template]    Match Count Should Be
    2    ${STRINGS}    regexp=.*a.*
    1    ${STRINGS}    regexp=wOrD
    2    ${STRINGS}    regexp=word     case_insensitive=True
    2    ${STRINGS}    regexp=wo.*     case_insensitive=True
    7    ${STRINGS}    regexp=[a-z]    case_insensitive=True
    13   ${STRINGS}    regexp=.*       case_insensitive=False
    6    ${STRINGS}    regexp=.$       case_insensitive=No

Count Matches In List Glob
    [Template]    Match Count Should Be
    2    ${STRINGS}    glob=*a*
    1    ${STRINGS}    glob=wOrD
    2    ${STRINGS}    glob=word    case_insensitive=yes
    2    ${STRINGS}    glob=wo*     case_insensitive=please
    13   ${STRINGS}    glob=*       case_insensitive=
    6    ${STRINGS}    glob=?       case_insensitive=${FALSE}

Get Matches In List Case Insensitive
    [Template]    List Should Equal Matches
    ${STRINGS}    a       ${False}    ${False}    a
    ${STRINGS}    A       ${True}    ${False}     a
    ${STRINGS}    A       ${False}    ${False}
    ${STRINGS}    word    ${True}    ${False}     wOrD    WOrd
    ${STRINGS}    b       ${True}    ${False}     B       b
    ${STRINGS}    b       ${False}    ${False}    b

Get Matches In List Whitespace Insensitive
    [Template]    List Should Equal Matches
    ${WHITESPACE_STRINGS}    word    ${False}   ${True}    w o r d    w\no\nr\nd    w\no r\nd
    ${WHITESPACE_STRINGS}    word    ${True}    ${True}    w o r d    w\no\nr\nd    w\no r\nd    W O R D
    ${WHITESPACE_STRINGS}    words   ${True}    ${True}

Get Matches In List Regexp
    [Template]    List Should Equal Matches
    ${STRINGS}    regexp=.*a.*    ${False}    ${False}    a      regexp=blah
    ${STRINGS}    regexp=wOrD     ${False}    ${False}    wOrD
    ${STRINGS}    regexp=word     ${True}     ${False}    wOrD    WOrd
    ${STRINGS}    regexp=wo.*     ${True}     ${False}    wOrD    WOrd
    ${STRINGS}    regexp=[a-z]    ${True}     ${False}    a       B    b    wOrD    WOrd    regexp=blah    glob=test
    ${STRINGS}    regexp=.*       ${False}    ${False}    @{STRINGS}
    ${STRINGS}    regexp=.$       ${False}    ${False}    a       B    b    1    2    3

Get Matches In List Glob
    [Template]    List Should Equal Matches
    ${STRINGS}    glob=*a*     ${False}    ${False}    a       regexp=blah
    ${STRINGS}    glob=wOrD    ${False}    ${False}    wOrD
    ${STRINGS}    glob=word    ${True}     ${False}    wOrD    WOrd
    ${STRINGS}    glob=wo*     ${True}     ${False}    wOrD    WOrd
    ${STRINGS}    glob=*       ${False}    ${False}    @{STRINGS}
    ${STRINGS}    glob=?       ${False}    ${False}    a       B    b    1    2    3

List Should Contain Value Case Insensitive
    [Template]    Should Contain Match
    ${STRINGS}    a
    ${STRINGS}    a       case_insensitive=True
    ${STRINGS}    A       case_insensitive=True
    ${STRINGS}    b       case_insensitive=True
    ${STRINGS}    B       case_insensitive=True
    ${STRINGS}    word    case_insensitive=True
    ${STRINGS}    WORD    case_insensitive=True
    ${STRINGS}    WoRd    case_insensitive=True
    ${STRINGS}    \${cmd list}

List Should Contain Value Whitespace Insensitive
    [Template]    Should Contain Match
    ${WHITESPACE_STRINGS}    word           whitespace_insensitive=1    case_insensitive=${0}
    ${WHITESPACE_STRINGS}    wOrD           whitespace_insensitive=2    case_insensitive=${1}
    ${WHITESPACE_STRINGS}    regexp=wo.*    whitespace_insensitive=3
    ${WHITESPACE_STRINGS}    regexp=Wo.*    whitespace_insensitive=4    case_insensitive=${2}
    ${WHITESPACE_STRINGS}    glob=wo*       whitespace_insensitive=5
    ${WHITESPACE_STRINGS}    glob=Wo*       whitespace_insensitive=6    case_insensitive=${3}

List Should Contain Value Regexp
    [Template]    Should Contain Match
    ${STRINGS}    regexp=.*a.*
    ${STRINGS}    regexp=wOrD
    ${STRINGS}    regexp=word     case_insensitive=True
    ${STRINGS}    regexp=wo.*     case_insensitive=True
    ${STRINGS}    regexp=[a-z]    case_insensitive=True
    ${STRINGS}    regexp=[a-zA-Z]
    ${STRINGS}    regexp=.*
    ${STRINGS}    regexp=\\w{4}
    ${STRINGS}    regexp=glob=.*

List Should Contain Value Glob
    [Template]    Should Contain Match
    ${STRINGS}    glob=*a*
    ${STRINGS}    glob=wOrD
    ${STRINGS}    glob=word        case_insensitive=True
    ${STRINGS}    glob=wo*         case_insensitive=True
    ${STRINGS}    glob=*
    ${STRINGS}    glob=?
    ${STRINGS}    glob=????
    ${STRINGS}    glob=?O??
    ${STRINGS}    glob=?o??        case_insensitive=True
    ${STRINGS}    glob=regexp=*    case_insensitive=True

List Should Contain Value, Value Not Found Case Insensitive
    [Documentation]    FAIL [ wOrD ] does not contain match for pattern 'words'.
    Should Contain Match    ${STRING}    words    case_insensitive=True

List Should Contain Value, Value Not Found Whitespace Insensitive
    [Documentation]    FAIL [ w o r d | w\no\nr\nd | w\no r\nd | W O R D ] does not contain match for pattern 'words'.
    Should Contain Match    ${WHITESPACE_STRINGS}    words    whitespace_insensitive=True

List Should Contain Value, Value Not Found Regexp
    [Documentation]    FAIL [ wOrD ] does not contain match for pattern 'regexp=wOrD.'.
    Should Contain Match    ${STRING}    regexp=wOrD.

List Should Contain Value, Value Not Found Glob
    [Documentation]    FAIL [ wOrD ] does not contain match for pattern 'glob=wOrD?'.
    Should Contain Match    ${STRING}    glob=wOrD?

List Should Contain Value, Value Not Found And Own Error Message Case Insensitive
    [Documentation]    FAIL My error message!
    Should Contain Match    ${STRING}    words    My error message!    case_insensitive=True

List Should Contain Value, Value Not Found And Own Error Message Whitespace Insensitive
    [Documentation]    FAIL My error message!
    Should Contain Match    ${WHITESPACE_STRINGS}    words    My error message!    whitespace_insensitive=True

List Should Contain Value, Value Not Found And Own Error Message Regexp
    [Documentation]    FAIL My error message!
    Should Contain Match    ${STRING}    regexp=wOrD.    My error message!

List Should Contain Value, Value Not Found And Own Error Message Glob
    [Documentation]    FAIL My error message!
    Should Contain Match    ${STRING}    glob=wOrD?    My error message!

List Should Not Contain Value Case Insensitive
    [Template]    Should Not Contain Match
    ${STRINGS}    words    case_insensitive=True
    ${STRINGS}    5        case_insensitive=True
    ${STRINGS}    word
    ${STRINGS}    AB       case_insensitive=True

List Should Not Contain Value Whitespace Insensitive
    [Template]    Should Not Contain Match
    ${WHITESPACE_STRINGS}    wOrD
    ${WHITESPACE_STRINGS}    wOrD                whitespace_insensitive=True
    ${WHITESPACE_STRINGS}    wOrDs               whitespace_insensitive=True    case_insensitive=True
    ${WHITESPACE_STRINGS}    regexp=.*words.*
    ${WHITESPACE_STRINGS}    regexp=.*words.*    whitespace_insensitive=True
    ${WHITESPACE_STRINGS}    regexp=.*words.*    whitespace_insensitive=True    case_insensitive=True
    ${WHITESPACE_STRINGS}    glob=*words*
    ${WHITESPACE_STRINGS}    glob=*words*        whitespace_insensitive=True
    ${WHITESPACE_STRINGS}    glob=*words*        whitespace_insensitive=True    case_insensitive=True

List Should Not Contain Value Regexp
    [Template]    Should Not Contain Match
    ${STRINGS}    regexp=.*words.*
    ${STRINGS}    regexp=[5-7]
    ${STRINGS}    regexp=.*word.*
    ${STRINGS}    regexp=(AB)         case_insensitive=True
    ${STRINGS}    regexp=\\w{9}

List Should Not Contain Value Glob
    [Template]    Should Not Contain Match
    ${STRINGS}    glob=*words*    case_insensitive=True
    ${STRINGS}    glob=[5]        case_insensitive=True
    ${STRINGS}    glob=*word?
    ${STRINGS}    glob=AB*        case_insensitive=True

List Should Not Contain Value, Value Found Case Insensitive
    [Documentation]    FAIL [ wOrD ] contains match for pattern 'word'.
    Should Not Contain Match    ${STRING}    word    case_insensitive=True

List Should Not Contain Value, Value Found Whitespace Insensitive
    [Documentation]    FAIL [ w o r d | w\no\nr\nd | w\no r\nd | W O R D ] contains match for pattern 'word'.
    Should Not Contain Match    ${WHITESPACE_STRINGS}    word    whitespace_insensitive=True

List Should Not Contain Value, Value Found Regexp
    [Documentation]    FAIL [ wOrD ] contains match for pattern 'regexp=.*w.*'.
    Should Not Contain Match    ${STRING}    regexp=.*w.*

List Should Not Contain Value, Value Found Glob
    [Documentation]    FAIL [ wOrD ] contains match for pattern 'glob=*'.
    Should Not Contain Match    ${STRING}    glob=*

List Should Not Contain Value, Value Found And Own Error Message Case Insensitive
    [Documentation]    FAIL My error message!
    Should Not Contain Match    ${STRING}    word    My error message!    case_insensitive=True

List Should Not Contain Value, Value Found And Own Error Message Regexp
    [Documentation]    FAIL My error message!
    Should Not Contain Match    ${STRING}    regexp=.*w.*    My error message!

List Should Not Contain Value, Value Found And Own Error Message Glob
    [Documentation]    FAIL My error message!
    Should Not Contain Match    ${STRING}    glob=*    My error message!

*** Keywords ***
Create Lists For The Tests
    ${L0} =    Create List
    Set Test Variable    \${L0}
    ${L1} =    Create List    1
    Set Test Variable    \${L1}
    ${L2} =    Create List    1    ${2}
    Set Test Variable    \${L2}
    ${L3} =    Create List    11    ${12}    13
    Set Test Variable    \${L3}
    ${L3B} =    Create List    10    12    14
    Set Test Variable    \${L3B}
    ${L4} =    Create List    41    ${42}    43    44
    Set Test Variable    \${L4}
    ${LONG} =    Combine Lists    ${L1}    ${L2}    ${L4}    ${L2}
    Set Test Variable    \${LONG}
    ${STRINGS} =    Create List    a    B    b    wOrD    WOrd
    ...    !@#$%^&*()_+-=    \${cmd list}    1    2    3    äö
    ...    regexp=blah    glob=test
    Set Test Variable    \${STRINGS}
    ${STRING} =    Create List    wOrD
    Set Test Variable    \${STRING}
    ${WHITESPACE_STRINGS} =    Create List    w o r d    w\no\nr\nd    w\no r\nd    W O R D
    Set Test Variable    \${WHITESPACE_STRINGS}

Insert Into List And Compare
    [Arguments]    ${list}    ${index}    ${value}    ${expected}
    Insert Into List    ${list}    ${index}    ${value}
    Compare To Expected String    ${list}    ${expected}

Get Random Item And Add It To List
    [Arguments]    ${from list}    ${to list}
    ${item} =    Get Item From List    Ran Dom    ${from list}
    Add Item To List    ${to list}    ${item}

Match Count Should Be
    [Arguments]    ${count}    ${list}    ${pattern}    ${case_insensitive}=${False}    ${whitespace_insensitive}=${False}
    ${actual_count} =    Get Match Count    ${list}    ${pattern}    ${case_insensitive}    ${whitespace_insensitive}
    Should Be Equal As Integers    ${count}    ${actual_count}    msg=Expected ${count} matches, got ${actual_count} matches for pattern '${pattern}' in ${list}

List Should Equal Matches
    [Arguments]    ${list_to_search}    ${pattern}    ${case_insensitive}=${False}    ${whitespace_insensitive}=${False}    @{list}
    ${list} =    Create List    @{list}
    ${matches} =    Get Matches    ${list_to_search}    ${pattern}    ${case_insensitive}    ${whitespace_insensitive}
    Lists Should Be Equal    ${matches}    ${list}
