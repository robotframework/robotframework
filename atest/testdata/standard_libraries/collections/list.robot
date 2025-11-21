*** Settings ***
Test Setup         Create Lists for the Tests
Library            Collections

*** Variables ***
${INDEX ERROR}     ValueError: Argument 'index' got value 'invalid' that cannot be converted to integer.
${START ERROR}     ValueError: Argument 'start' got value 'invalid' that cannot be converted to integer.
${START ERROR2}    ValueError: Argument 'start' got value 'invalid' that cannot be converted to integer or ''.
${END ERROR}       ValueError: Argument 'end' got value 'invalid' that cannot be converted to integer or None.
${OUT OF RANGE}    IndexError: Given index 10 is out of the range 0-2.
${TUPLE: tuple}    ('1', 2)
${DICT: dict}      {'a': 1, 2: 'b'}
${SET: set}        {'x'}

*** Test Cases ***
Convert To List
    [Template]    Verify Result
    Convert To List    hello      expected=['h', 'e', 'l', 'l', 'o']
    Convert To List   ${TUPLE}    expected=['1', 2]
    Convert To List   ${DICT}     expected=['a', 2]
    Convert To List   ${SET}      expected=['x']

Convert To List With Invalid Type
    [Template]    Verify Error
    Convert To List    ${1}       expected=STARTS: TypeError:
    Convert To List    ${None}    expected=STARTS: TypeError:

Append To List
    [Template]    Verify Modification
    Append To List    ${L0}    1              expected=['1']
    Append To List    ${L0}    2    3    4    expected=['1', '2', '3', '4']

Append To List with immutable
    [Template]    Verify Result
    Append To List    ('a', 'b')    c              expected=['a', 'b', 'c']
    Append To List    ('a', 'b')    c    d    e    expected=['a', 'b', 'c', 'd', 'e']

Insert Into List
    [Template]    Verify Modification
    Insert Into List    ${L2}    1       v1    expected=['1', 'v1', 2]
    Insert Into List    ${L2}    ${1}    v2    expected=['1', 'v2', 'v1', 2]
    Insert Into List    ${L2}    1000    v3    expected=['1', 'v2', 'v1', 2, 'v3']
    Insert Into List    ${L2}    -2      v4    expected=['1', 'v2', 'v1', 'v4', 2, 'v3']

Insert Into List with immutable
    [Template]    Verify Result
    Insert Into List    ('a', 'c')    1    b    expected=['a', 'b', 'c']

Insert Into List with invalid index
    [Template]    Verify Error
    Insert Into List    ${L3}    invalid    value    expected=${INDEX ERROR}

Combine Lists
    [Template]    Verify Result
    Combine Lists    ${L1}    ${L2}                      expected=['1', '1', 2]
    Combine Lists    ${L1}    ${L2}    ${L3}    ${L0}    expected=['1', '1', 2, '11', 12, '13']
    Combine Lists    ${TUPLE}    ${DICT}    ${SET}       expected=['1', 2, 'a', 2, 'x']

Set List Value
    [Template]    Verify Modification
    Set List Value    ${L3}    1       v1    expected=['11', 'v1', '13']
    Set List Value    ${L3}    ${1}    v2    expected=['11', 'v2', '13']
    Set List Value    ${L3}    -1      v3    expected=['11', 'v2', 'v3']

Set List Value with immutable
    [Template]    Verify Result
    Set List Value    ('a', 'b', 'c')    1    B    expected=['a', 'B', 'c']

Set List Value with invalid index
    [Template]    Verify Error
    Set List Value    ${L3}    10         whatever     expected=${OUT OF RANGE}
    Set List Value    ${L3}    invalid    whatever     expected=${INDEX ERROR}

Remove Values From List
    [Template]    Verify Modification
    Remove Values From List    ${LONG}    ${42}        expected=['1', '1', 2, '41', '43', '44', '1', 2]
    Remove Values From List    ${LONG}    1    ${2}    expected=['41', '43', '44']
    Remove Values From List    ${LONG}    nonex        expected=['41', '43', '44']

Remove Values From List with immutable
    [Template]    Verify Result
    Remove Values From List    (1, 2, 2, 3, 2, 4)    ${2}    expected=[1, 3, 4]

Remove From List
    [Template]    Verify Modification
    Remove From List    ${L3}    ${1}    expected=['11', '13']    result=${12}
    Remove From List    ${L3}    -2      expected=['13']          result=11

Remove From List with immutable
    [Template]    Verify Result
    Remove From List    ('a', 'b', 'c')    ${1}    expected=b     type=str
    Remove From List    (-1, -2, -3)       1       expected=-2    type=int

Remove From List with invalid index
    [Template]    Verify Error
    Remove From List    ${L3}    10         expected=${OUT OF RANGE}
    Remove From List    ${L3}    invalid    expected=${INDEX ERROR}

Remove Duplicates
    [Template]    Verify Result
    Remove Duplicates    ${L3}      expected=${L3}
    Remove Duplicates    ${LONG}    expected=['1', 2, '41', 42, '43', '44']

Count Values In List
    [Template]    Verify Result
    Count Values In List    ${LONG}    1              expected=3    type=int
    Count Values In List    ${LONG}    ${2}           expected=2    type=int
    Count Values In List    ${LONG}    1    3         expected=1    type=int
    Count Values In List    ${LONG}    1    0    4    expected=2    type=int

Count Values In List with invalid index
    [Template]    Verify Error
    Count Values In List    ${LONG}    2    invalid    1    expected=${START ERROR}
    Count Values In List    ${LONG}    2    1    invalid    expected=${END ERROR}

Get Index From List
    [Template]    Verify Result
    Get Index From List    ${LONG}    ${2}            expected=2     type=int
    Get Index From List    ${LONG}    ${2}    3       expected=8     type=int
    Get Index From List    ${LONG}    43    4    7    expected=5     type=int
    Get Index From List    ${LONG}    43   end=8      expected=5     type=int
    Get Index From List    ${LONG}    nonex           expected=-1    type=int

Get Index From List with empty string as start index is deprecated
    [Template]    Verify Result
    Get Index From List    ${LONG}    43    ${EMPTY}    8    expected=5     type=int

Get Index From List with invalid index
    [Template]    Verify Error
    Get Index From List    ${LONG}    2    invalid    1     expected=${START ERROR2}
    Get Index From List    ${LONG}    2    1    invalid     expected=${END ERROR}

Copy List
    ${copy} =    Copy List    ${L2}
    Append To List    ${L2}      add to original
    Append To List    ${copy}    add to copy
    Should Be Equal    ${copy}    ['1', 2, 'add to copy']    type=list

Shallow Copy List
    VAR    &{dict}    a=1
    VAR    @{list}    ${dict}
    ${copy} =    Copy List    ${list}
    Set To Dictionary    ${dict}    a    2
    Should Be Equal    ${list}[0][a]    2
    Should Be Equal    ${copy}[0][a]    2

Deep Copy List
    VAR    &{dict}    a=1
    VAR    @{list}    ${dict}
    ${copy} =    Copy List    ${list}    deepcopy=True
    Set To Dictionary    ${dict}    a    2
    Should Be Equal    ${list}[0][a]    2
    Should Be Equal    ${copy}[0][a]    1

Reverse List
    [Template]    Verify Modification
    Reverse List    ${LONG}    expected=[2, '1', '44', '43', 42, '41', 2, '1', '1']

Reverse List with immutable
    [Template]    Verify Result
    Reverse List    (1, 'a', None)    expected=[None, 'a', 1]

Sort List
    [Template]    Verify Modification
    Sort List    ${{[]}}                     expected=[]
    Sort List    ${{[3, -1, 0.1, 0, 42]}}    expected=[-1, 0, 0.1, 3, 42]

Sort List with immutable
    [Template]    Verify Result
    Sort List    ()                     expected=[]
    Sort List    (3, -1, 0.1, 0, 42)    expected=[-1, 0, 0.1, 3, 42]

Sorting unsortable list fails
    [Template]    Verify Error
    Sort List    ${{[complex(1), complex(2)]}}    expected=STARTS: TypeError:

Get From List
    [Template]    Verify Result
    Get From List    ${L4}    1     expected=42    type=int
    Get From List    ${L4}    -2    expected=43    type=str

Get From List with invalid index
    [Template]    Verify Error
    Get From List    ${L3}    invalid    expected=${INDEX ERROR}
    Get From List    ${L3}    10         expected=${OUT OF RANGE}

Get Slice From List
    [Template]    Verify Result
    Get Slice From List    ${L4}                expected=${L4}
    Get Slice From List    ${L4}    1           expected=[42, '43', '44']
    Get Slice From List    ${L4}    1    2      expected=[42]
    Get Slice From List    ${L4}    end=2       expected=['41', 42]
    Get Slice From List    ${L4}    100         expected=[]
    Get Slice From List    ${L4}    2    100    expected=['43', '44']

Get Slice From List with empty string as start index is deprecated
    [Template]    Verify Result
    Get Slice From List    ${L4}    ${EMPTY}    2    expected=['41', 42]

Get Slice From List with invalid index
    [Template]    Verify Error
    Get Slice From List    ${L4}    invalid    2    expected=${START ERROR2}
    Get Slice From List    ${L4}    2    invalid    expected=${END ERROR}

List Should Contain Value
    List Should Contain Value    ${L1}      1
    List Should Contain Value    ${DICT}    a

List Should Contain Value, Value Not Found
    [Documentation]    FAIL [ 1 ] does not contain value '2'.
    List Should Contain Value    ${L1}    2

List Should Contain Value, Value Not Found And Own Error Message
    [Documentation]    FAIL My error message!
    List Should Contain Value    ${L1}    2    My error message!

List Should Not Contain Value
    List Should Not Contain Value    ${L1}      2
    List Should Not Contain Value    ${DICT}    2

List Should Not Contain Value, Value Found
    [Documentation]    FAIL [ 1 ] contains value '1'.
    List Should Not Contain Value    ${L1}    1

List Should Not Contain Value, Value Found And Own Error Message
    [Documentation]    FAIL My error message!
    List Should Not Contain Value    ${L1}    1    My error message!

List Should Not Contain Duplicates With No Duplicates
    FOR    ${list}    IN    ${L0}    ${L1}    ${L2}    ${L3}    ${L4}    ${TUPLE}
        List Should Not Contain Duplicates    ${list}
    END

List Should Not Contain Duplicates Is Case And Space Sensitive
    VAR    @{list}    item    ITEM    i tem    i t e m    ITE_m
    List Should Not Contain Duplicates    ${list}

List Should Not Contain Duplicates With One Duplicate
    [Documentation]    FAIL 'item' found multiple times.
    VAR    @{list}    item    item    another item    fourth item    ITEM
    List Should Not Contain Duplicates    ${list}

List Should Not Contain Duplicates With Multiple Duplicates
    [Documentation]    FAIL '2', 'None', '4', '[1, 2, 3]' and '[]' found multiple times.
    ${list} =    Evaluate    [1, 2, '2', 2, None, '4', '4', '4', '4', '42', [1, 2, 3], {}, False] + [[]]*10 + [[1, 2, 3], None, (1, 2, 3, 4), 'a', 'A']
    List Should Not Contain Duplicates    ${list}

List Should Not Contain Duplicates With Custom Error Message
    [Documentation]    FAIL My special error
    List Should Not Contain Duplicates    ${L0}           Not used custom error
    List Should Not Contain Duplicates    ${{[6] * 7}}    My special error

Lists Should Be Equal
    [Template]    Lists Should Be Equal
    ${L0}        ${L0}
    ${L2}        ${L2}
    ${LONG}      ${LONG}
    ${TUPLE}     ${L2}
    ${L2}        ${TUPLE}
    ${DICT}      ['a', 2]
    ${SET}       ['x']
    (1, 2, 3)    [1, 2, 3]

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
    Lists Should Be Equal    ${L3}    ${L3B}    names=['a', 'b', 'c', 'ignored']

Lists Should Be Equal With Named Indices As List With Too Few Values
    [Documentation]    FAIL My message
    ...    Lists are different:
    ...    Index 0 (a): 11 != 10
    ...    Index 1 (b): 12 (integer) != 12 (string)
    ...    Index 2: 13 != 14
    Lists Should Be Equal    ${L3}    ${L3B}    My message    names=${{['a', 'b']}}

Lists Should Be Equal With Named Indices As Dictionary
    [Documentation]    FAIL Lists are different:
    ...    Index 0 (a): 11 != 10
    ...    Index 1 (b): 12 (integer) != 12 (string)
    ...    Index 2 (c): 13 != 14
    Lists Should Be Equal    ${L3}    ${L3B}    names={0: 'a', '1': 'b', 2: 'c', 42: 'ignored'}

Lists Should Be Equal With Named Indices As Dictionary With Too Few Values
    [Documentation]    FAIL Lists are different:
    ...    Index 0 (a): 11 != 10
    ...    Index 1: 12 (integer) != 12 (string)
    ...    Index 2 (c): 13 != 14
    Lists Should Be Equal    ${L3}    ${L3B}    names=${{{0: 'a', '2': 'c'}}}

Lists Should Be Equal Ignore Order
    VAR    @{list1}    A    B    C    D
    VAR    @{list2}    D    B    C    A
    Lists Should Be Equal    ${list1}    ${list2}    ignore_order=True

Ignore Order Is Recursive
    Lists Should Be Equal    [(1, 2, 3), (4, 5, 6)]    [(6, 4, 5), (3, 1, 2)]    ignore_order=yes

List Should Contain Sub List
    List Should Contain Sub List    ${LONG}    ${L4}

List Should Contain Sub List With Missing Values
    [Documentation]    FAIL Following values are missing: '1', '1', '2', '1' and '2'
    List Should Contain Sub List    ${L4}    ${LONG}

List Should Contain Sub List When The Only Missing Value Is Empty String
    [Documentation]    FAIL Following values are missing: ''
    List Should Contain Sub List    ${L4}    ${{['41', 42, '', '43']}}

List Should Contain Sub List With Missing Values And Own Error Message
    [Documentation]    FAIL My error message!
    List Should Contain Sub List    ${L4}    ${LONG}    My error message!    values=no

List Should Contain Sub List With Missing Values And Own And Default Error Messages
    [Documentation]    FAIL My error message!
    ...    Following values are missing: 'x' and 'y'
    List Should Contain Sub List    ${L4}    ${{'x', 'y'}}    My error message!    values=please

'NO VALUES' is deprecated
    [Documentation]    FAIL Message
    Lists Should Be Equal    ${L4}    ${L4}    values=NO VALUES
    List Should Contain Sub List    ${L4}    ${LONG}    Message    no values

Log List
    Log List    ${L0}
    Log List    ${{tuple($L3)}}
    Log List    ${L3}    INFO
    Log List    ${L3}    tRAce
    Log List    ${L3}    warn
    Log List    ${L3}    DEbug

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
    ${STRINGS}    A       ${True}     ${False}    a
    ${STRINGS}    A       False       false
    ${STRINGS}    word    yes         no          wOrD    WOrd
    ${STRINGS}    b       1           0           B       b
    ${STRINGS}    b       no          NO          b

Get Matches In List Whitespace Insensitive
    [Template]    List Should Equal Matches
    ${WHITESPACE_STRINGS}    word    False      True    w o r d    w\no\nr\nd    w\no r\nd
    ${WHITESPACE_STRINGS}    word    ${True}    ${True}    w o r d    w\no\nr\nd    w\no r\nd    W O R D
    ${WHITESPACE_STRINGS}    words   yes        yes

Get Matches In List Regexp
    [Template]    List Should Equal Matches
    ${STRINGS}    regexp=.*a.*    False       False       a      regexp=blah
    ${STRINGS}    regexp=wOrD     ${False}    ${False}    wOrD
    ${STRINGS}    regexp=word     true        false       wOrD    WOrd
    ${STRINGS}    regexp=wo.*     yes         no          wOrD    WOrd
    ${STRINGS}    regexp=[a-z]    True        False       a       B    b    wOrD    WOrd    regexp=blah    glob=test
    ${STRINGS}    regexp=.*       0           0           @{STRINGS}
    ${STRINGS}    regexp=.$       ${0}        ${0}        a       B    b    1    2    3

Get Matches In List Glob
    [Template]    List Should Equal Matches
    ${STRINGS}    glob=*a*     False       False       a       regexp=blah
    ${STRINGS}    glob=wOrD    false       false       wOrD
    ${STRINGS}    glob=word    yes         no          wOrD    WOrd
    ${STRINGS}    glob=wo*     ${1}        ${0}        wOrD    WOrd
    ${STRINGS}    glob=*       False       FALSE       @{STRINGS}
    ${STRINGS}    glob=?       ${False}    ${False}    a       B    b    1    2    3

List Should Contain Value Case Insensitive
    [Template]    Should Contain Match
    ${STRINGS}    a
    ${STRINGS}    \${cmd list}
    # Old config.
    ${STRINGS}    a       case_insensitive=True
    ${STRINGS}    A       case_insensitive=yes
    ${STRINGS}    b       case_insensitive=${True}
    ${STRINGS}    B       case_insensitive=xxx
    ${STRINGS}    word    case_insensitive=${1}
    ${STRINGS}    WORD    case_insensitive=TRUE
    ${STRINGS}    WoRd    case_insensitive=true
    # New config.
    ${STRINGS}    a       ignore_case=True
    ${STRINGS}    A       ignore_case=yes
    ${STRINGS}    b       ignore_case=${True}
    ${STRINGS}    B       ignore_case=xxx
    ${STRINGS}    word    ignore_case=${1}
    ${STRINGS}    WORD    ignore_case=TRUE
    ${STRINGS}    WoRd    ignore_case=true

List Should Contain Value Whitespace Insensitive
    [Template]    Should Contain Match
    # Old config.
    ${WHITESPACE_STRINGS}    word           whitespace_insensitive=1    case_insensitive=${0}
    ${WHITESPACE_STRINGS}    wOrD           whitespace_insensitive=2    case_insensitive=${1}
    ${WHITESPACE_STRINGS}    regexp=wo.*    whitespace_insensitive=3
    ${WHITESPACE_STRINGS}    regexp=Wo.*    whitespace_insensitive=4    case_insensitive=${2}
    ${WHITESPACE_STRINGS}    glob=wo*       whitespace_insensitive=5
    ${WHITESPACE_STRINGS}    glob=Wo*       whitespace_insensitive=6    case_insensitive=${3}
    # New config.
    ${WHITESPACE_STRINGS}    word           ignore_whitespace=1    ignore_case=${0}
    ${WHITESPACE_STRINGS}    wOrD           ignore_whitespace=2    ignore_case=${1}
    ${WHITESPACE_STRINGS}    regexp=wo.*    ignore_whitespace=3
    ${WHITESPACE_STRINGS}    regexp=Wo.*    ignore_whitespace=4    ignore_case=${2}
    ${WHITESPACE_STRINGS}    glob=wo*       ignore_whitespace=5
    ${WHITESPACE_STRINGS}    glob=Wo*       ignore_whitespace=6    ignore_case=${3}

List Should Contain Value Regexp
    [Template]    Should Contain Match
    ${STRINGS}    regexp=.*a.*
    ${STRINGS}    regexp=wOrD
    ${STRINGS}    regexp=word     case_insensitive=True
    ${STRINGS}    regexp=wo.*     case_insensitive=yes
    ${STRINGS}    regexp=[a-z]    case_insensitive=${1}
    ${STRINGS}    regexp=[a-zA-Z]
    ${STRINGS}    regexp=.*
    ${STRINGS}    regexp=\\w{4}
    ${STRINGS}    regexp=glob=.*

List Should Contain Value Glob
    [Template]    Should Contain Match
    ${STRINGS}    glob=*a*
    ${STRINGS}    glob=wOrD
    ${STRINGS}    glob=word        case_insensitive=True
    ${STRINGS}    glob=wo*         case_insensitive=true
    ${STRINGS}    glob=*
    ${STRINGS}    glob=?
    ${STRINGS}    glob=????
    ${STRINGS}    glob=?O??
    ${STRINGS}    glob=?o??        case_insensitive=yes
    ${STRINGS}    glob=regexp=*    case_insensitive=xxx

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
    ${STRINGS}    word
    # Old config.
    ${STRINGS}    words    case_insensitive=True
    ${STRINGS}    5        case_insensitive=yes
    ${STRINGS}    AB       case_insensitive=${True}
    # New config.
    ${STRINGS}    words    ignore_case=True
    ${STRINGS}    5        ignore_case=yes
    ${STRINGS}    AB       ignore_case=${True}

List Should Not Contain Value Whitespace Insensitive
    [Template]    Should Not Contain Match
    ${WHITESPACE_STRINGS}    wOrD
    ${WHITESPACE_STRINGS}    regexp=.*words.*
    ${WHITESPACE_STRINGS}    glob=*words*
    # Old config.
    ${WHITESPACE_STRINGS}    wOrD                whitespace_insensitive=True
    ${WHITESPACE_STRINGS}    wOrDs               whitespace_insensitive=true    case_insensitive=true
    ${WHITESPACE_STRINGS}    regexp=.*words.*    whitespace_insensitive=${True}
    ${WHITESPACE_STRINGS}    regexp=.*words.*    whitespace_insensitive=yes     case_insensitive=yes
    ${WHITESPACE_STRINGS}    glob=*words*        whitespace_insensitive=1
    ${WHITESPACE_STRINGS}    glob=*words*        whitespace_insensitive=${1}    case_insensitive=${2}
    # New config.
    ${WHITESPACE_STRINGS}    wOrD                ignore_whitespace=True
    ${WHITESPACE_STRINGS}    wOrDs               ignore_whitespace=true         ignore_case=true
    ${WHITESPACE_STRINGS}    regexp=.*words.*    ignore_whitespace=${True}
    ${WHITESPACE_STRINGS}    regexp=.*words.*    ignore_whitespace=yes          ignore_case=yes
    ${WHITESPACE_STRINGS}    glob=*words*        ignore_whitespace=1
    ${WHITESPACE_STRINGS}    glob=*words*        ignore_whitespace=${1}         ignore_case=${2}

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
    ${STRINGS}    glob=[5]        case_insensitive=yes
    ${STRINGS}    glob=*word?
    ${STRINGS}    glob=AB*        case_insensitive=${True}

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

Lists Should Be Equal With Ignore Case
    [Template]    Lists Should Be Equal
    ${L0}                       ${L0}                        ignore_case=True
    ${LONG}                     ${LONG}                      ignore_case=True
    \['a', 'b', 'c', 1, 2]       ['A', 'B', 'C', 1, 2]       ignore_case=True
    (['a', {'b': 'c'}], 'd')     [['A', {'B': 'C'}], 'D']    ignore_case=True

List Should Contain Value With Ignore Case
    List Should Contain Value    ['a', 'b']    value=A    ignore_case=True

List Should Not Contain Value With Ignore Case Does Contain Value
    [Documentation]  FAIL [ a | b ] contains value 'A'.
    List Should Not Contain Value    ['a', 'b']    value=A    ignore_case=True

List Should Contain Sub List With Ignore Case
    List Should Contain Sub List    ['A', 'b', 'C']    ['B', 'c']    ignore_case=True

List Should Not Contain Duplicates With Ignore Case
    [Documentation]    FAIL 'a' and 'c' found multiple times.
    List Should Not Contain Duplicates    ['A', 'B', 'C', 'a', 'c']    ignore_case=True

List Should Contain Value With Ignore Case And Nested List and Dictionary
    List Should Contain Value    ['a', ['b', 'c']]    ${{['B', 'C']}}    ignore_case=True

Lists Should be equal with Ignore Case and Order
    [Template]    Lists Should Be Equal
    \['a', 'b', 'c']    ['B', 'C', 'A']    ignore_case=True    ignore_order=True
    \[('A', 'B')]       [('b', 'a')]       ignore_case=True    ignore_order=True

Validate argument conversion errors
    [Template]    Validate invalid argument error
    VAR                                   ${invalid_arg}              I am a string. Not a list.
    Append to list                        xyz                         annotation=Sequence: Invalid expression
    Combine Lists                         ${invalid_arg}              arg_name=lists
    Combine Lists                         ${L0}   ${invalid_arg}      arg_name=lists    invalid_argument=${invalid_arg}
    Combine Lists                         ${invalid_arg}    ${L0}     arg_name=lists
    Copy list                                                         annotation=Sequence: Invalid expression
    Count values in list                  ${invalid_arg}    xyz       annotation=Sequence: Invalid expression
    Get from list                         ${invalid_arg}    0         annotation=Sequence: Invalid expression
    Get Index From List                   ${invalid_arg}    a         annotation=Sequence: Invalid expression
    Get Match Count                       ${invalid_arg}    abc       arg_name=list
    Get Matches                           ${invalid_arg}    abc       arg_name=list
    Get slice from list                                               annotation=Sequence: Invalid expression
    Insert into list                      ${invalid_arg}    0    a    annotation=Sequence: Invalid expression
    List Should Contain Sub List          ${invalid_arg}    ${L0}     arg_name=list1
    List Should Contain Sub List          ${L0}    ${invalid_arg}     arg_name=list2    invalid_argument=${invalid_arg}
    List Should Contain Value             ${invalid_arg}    a
    List Should Not Contain Duplicates    xyz                         annotation=Sequence: Invalid expression
    List Should Not Contain Value         ${invalid_arg}    x
    Lists Should Be Equal                 ${invalid_arg}    ${L0}     arg_name=list1
    Lists Should Be Equal                 ${L0}    ${invalid_arg}     arg_name=list2    invalid_argument=${invalid_arg}
    Log List                                                          annotation=Sequence: Invalid expression
    Remove Duplicates                                                 annotation=Sequence: Invalid expression
    Remove From List                      ${invalid_arg}    0         annotation=Sequence: Invalid expression
    Remove Values From List               ${invalid_arg}    a         annotation=Sequence: Invalid expression
    Reverse List                                                      annotation=Sequence: Invalid expression
    Set List Value                        ${invalid_arg}    0    a    annotation=Sequence: Invalid expression
    Should Contain Match                  ${invalid_arg}    a         arg_name=list
    Should Not Contain Match              ${invalid_arg}    xyz       arg_name=list
    Sort List                                                         annotation=Sequence: Invalid expression

Bytes normalization
    [Documentation]    FAIL    'rf' found multiple times.
    List Should Contain Value             ${{[b'\x00', b'RF']}}    ${{b'rf'}}      ignore_case=True
    List Should Not Contain Duplicates    ${{[b'RF', b'rf']}}                      ignore_case=True

*** Keywords ***
Validate invalid argument error
    [Arguments]    ${keyword}    ${argument}=I'm not a list, I'm a string.    @{args}    ${arg_name}=list_    ${annotation}=Sequence, Mapping or set    ${invalid_argument}=${NONE}
    IF    not $invalid_argument
        VAR    ${invalid_argument}    ${argument}
    END
    Run Keyword And Expect Error
    ...    ValueError: Argument '${arg_name}' got value '${invalid_argument}' that cannot be converted to ${annotation}.
    ...    ${keyword}    ${argument}    @{args}

Create Lists For The Tests
    VAR    @{L0}                                             scope=TEST
    VAR    @{L1}         1                                   scope=TEST
    VAR    @{L2}         1        ${2}                       scope=TEST
    VAR    @{L3}         11       ${12}    13                scope=TEST
    VAR    @{L3B}        10       12       14                scope=TEST
    VAR    @{L4}         41       ${42}    43       44       scope=TEST
    VAR    @{LONG}       @{L1}    @{L2}    @{L4}    @{L2}    scope=TEST
    VAR    @{STRING}     wOrD                                scope=TEST
    VAR    @{STRINGS}    a    B    b    wOrD    WOrd
    ...    !@#$%^&*()_+-=    \${cmd list}    1    2    3
    ...    äö .    regexp=blah    glob=test    scope=TEST
    VAR    @{WHITESPACE STRINGS}
    ...    w o r d    w\no\nr\nd    w\no r\nd    W O R D     scope=TEST

Match Count Should Be
    [Arguments]    ${expected}    ${list}    ${pattern}    ${case_insensitive}=False    ${whitespace_insensitive}=False
    ${count} =    Get Match Count    ${list}    ${pattern}    ${case_insensitive}    ${whitespace_insensitive}
    Should Be Equal    ${count}    ${expected}    type=int
    ${count} =    Get Match Count    ${list}    ${pattern}    ignore_case=${case_insensitive}    ignore_whitespace=${whitespace_insensitive}
    Should Be Equal    ${count}    ${expected}    type=int

List Should Equal Matches
    [Arguments]    ${list_to_search}    ${pattern}    ${case_insensitive}=False    ${whitespace_insensitive}=False    @{list}
    ${matches} =    Get Matches    ${list_to_search}    ${pattern}    ${case_insensitive}    ${whitespace_insensitive}
    Lists Should Be Equal    ${matches}    ${list}
    ${matches} =    Get Matches    ${list_to_search}    ${pattern}    ignore_case=${case_insensitive}    ignore_whitespace=${whitespace_insensitive}
    Lists Should Be Equal    ${matches}    ${list}

Verify Modification
    [Arguments]    ${keyword}    ${list}    @{args}    ${expected}    ${result}=${None}
    ${actual} =    Run Keyword    ${keyword}    ${list}    @{args}
    Should Be Equal    ${list}      ${expected}    type=list
    IF    not $result
        VAR    ${result}    ${expected}
        VAR    ${type}      list
    ELSE
        VAR    ${type}      ${None}
    END
    Should Be Equal    ${actual}    ${result}    type=${type}

Verify Result
    [Arguments]    ${keyword}    @{args}    ${expected}    ${type}=list    &{named}
    ${actual} =    Run Keyword    ${keyword}    @{args}    &{named}
    Should Be Equal    ${actual}    ${expected}    type=${type}

Verify Error
    [Arguments]    ${keyword}    @{args}    ${expected}
    Run Keyword And Expect Error    ${expected}    ${keyword}    @{args}
