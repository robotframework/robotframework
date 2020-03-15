*** Settings ***
Library               Collections
Test Template         Dict Variable Should Be Equal

*** Variables ***
&{FIRST DICT EVER}    key=value    foo=bar
&{EMPTY DICT}
&{NÖN ÄSCII}          nön=äscii    snowman=\u2603
&{SPACES}             \ lead=    =trail \    \ \ 2 \ = \ \ 3 \ \ \
&{MANY ITEMS}         a=1     b=2     c=3     d=4     1=5     2=6     3=7
...                   e=8     f=9     g=10    X=11    Y=12    Z=13    h=14
...                   i=15    j=16    k=17    l=18    m=19    n=20    .=21
&{EQUALS}             key=value with=sign        empty value=    =    ===
&{ESCAPING EQUALS}    esc\=key=esc\=value    bs\\=\\    bs\\\=\\=    \===
&{EQUALS IN VAR}      ${{'='}}=value    ${{'='}}${{'='}}\=${{'='}}=${{'='}}
&{BAD SYNTAX 1}       this=good    this bad
...                   &{good}   @{bad}
&{BAD SYNTAX 2}       bad\=again
&{VARIABLES}          a=${1}    ${2}=b    ${True}=${False}
@{LIST}               ${1}    ${2}    ${3}
&{LIST VALUES}        scalar=${LIST}    list=@{LIST}
&{DICT AS LIST}       first=@{EMPTY DICT}    second=@{${NAME}}
&{DICT VALUES}        scalar=${FIRST DICT EVER}    dict=&{EMPTY DICT}
&{EXTENDED}           extended 1=&{FIRST DICT EVER.copy()}
...                   extended 2=&{FIRST DICT EVER.fromkeys([1, 2], 42)}
${NAME}               first dict ever
&{INTERNAL}           internal 1=&{${NAME}}
...                   internal 2=&{${NAME.upper()}.fromkeys([${1}, ${2}], ${42})}
&{OVERRIDE}           a=1    a=2    b=1    a=3    b=2    b=3    a=4    a=5
&{OVERRIDE W/ VARS}   ${1}=a    ${1.0}=b    ${0+1}=c    ${1*1}=d    ${1.00}=e    ${1+0}=f
&{USE DICT}           key=not    &{FIRST DICT EVER}    &{EMPTY DICT}    new=this    foo=that
&{USE DICT EXTENDED}  &{FIRST DICT EVER.copy()}    &{EMPTY DICT.fromkeys(['foo', 'new'])}
&{USE DICT INTERNAL}  &{${NAME}}    &{${NAME.upper()}.fromkeys(['foo', 'new'], ${40+2})}
&{NON HASHABLE KEY}   ${LIST}=doesn't work
&{NON DICT DICT 1}    name=&{LIST}
&{NON DICT DICT 2}    &{SPACE}
&{NON DICT DICT 3}    &{EMPTY DICT.keys()}

*** Test Cases ***
Dict variable
    ${FIRST DICT EVER}    {'key': 'value', 'foo': 'bar'}
    ${EMPTY DICT}         {}
    ${NÖN ÄSCII}          {u'nön': u'äscii', 'snowman': u'\\u2603'}
    ${SPACES}             {' lead': '', '': 'trail ', ' \ 2 \ ': ' \ \ 3 \ \ '}
    ${MANY ITEMS}         dict((k, str(i+1)) for i, k in enumerate('abcd123efgXYZhijklmn.'))

First non-escaped equal sign is separator
    ${EQUALS}             {'key': 'value with=sign', 'empty value': '', '': '=='}
    ${ESCAPING EQUALS}    {'esc=key': 'esc=value', 'bs\\\\': '\\\\', 'bs\\\\=\\\\': '', '=': '='}

Equals is not detected in variable name
    ${EQUALS IN VAR}      {'=': 'value', '====': '='}

Invalid syntax
    [Template]    Variable Should Not Exist
    ${BAD SYNTAX 1}
    ${BAD SYNTAX 2}

Variables in key and value
    ${VARIABLES}          {'a': 1, 2: 'b', True: False}
    ${LIST VALUES}        {'scalar': [1, 2, 3], 'list': [1, 2, 3]}
    ${DICT AS LIST}       {'first': [], 'second': @{FIRST DICT EVER}}
    ${DICT VALUES}        {'scalar': ${FIRST DICT EVER}, 'dict': {}}

Extended variables
    ${EXTENDED}           {'extended 1': ${FIRST DICT EVER}, 'extended 2': {1: 42, 2: 42}}

Internal variables
    ${INTERNAL}           {'internal 1': ${FIRST DICT EVER}, 'internal 2': {1: 42, 2: 42}}

Last item overrides
    ${OVERRIDE}           {'a': '5', 'b': '3'}
    ${OVERRIDE W/ VARS}   {1: 'f'}

Create from dict variable
    ${USE DICT}           {'key': 'value', 'foo': 'that', 'new': 'this'}
    ${USE DICT EXTENDED}  {'key': 'value', 'foo': None, 'new': None}
    ${USE DICT INTERNAL}  {'key': 'value', 'foo': 42, 'new': 42}

Dict from variable table should be ordered
    [Template]    NONE
    @{expected keys} =    Evaluate    list('abcd123efgXYZhijklmn.')
    @{expected values} =    Evaluate    [str(i+1) for i in range(21)]
    ${keys} =    Create List    @{MANY ITEMS}
    ${values} =    Create List    @{MANY ITEMS.values()}
    Should Be Equal    ${keys}    ${expected keys}
    Should Be Equal    ${values}    ${expected values}
    Set To Dictionary    ${MANY ITEMS}    a    new value
    Set To Dictionary    ${MANY ITEMS}    z    new item
    Append To List    ${expected keys}    z
    Set List Value    ${expected values}    0    new value
    Append To List    ${expected values}    new item
    ${keys} =    Create List    @{MANY ITEMS.keys()}
    ${values} =    Create List    @{MANY ITEMS.values()}
    Should Be Equal    ${keys}    ${expected keys}
    Should Be Equal    ${values}    ${expected values}

Dict from variable table should be dot-accessible
    [Template]    NONE
    Should Be Equal    ${FIRST DICT EVER.key}    value
    Should Be Equal    ${NÖN ÄSCII.snowman}    \u2603

Dict from variable table should be dot-assignable 1
    [Template]    NONE
    ${FIRST DICT EVER.key} =    Set Variable    new value
    ${NÖN ÄSCII.new_key} =    Set Variable    hyvä
    Should Be Equal    ${FIRST DICT EVER.key}    new value
    Should Be Equal    ${FIRST DICT EVER['key']}    new value
    Should Be Equal    ${NÖN ÄSCII.new_key}    hyvä
    Length Should Be    ${FIRST DICT EVER}    2
    Length Should Be    ${NÖN ÄSCII}    3

Dict from variable table should be dot-assignable 2
    [Template]    NONE
    Should Be Equal    ${FIRST DICT EVER.key}    new value
    Should Be Equal    ${FIRST DICT EVER['key']}    new value
    Should Be Equal    ${NÖN ÄSCII.new_key}    hyvä
    Length Should Be    ${FIRST DICT EVER}    2
    Length Should Be    ${NÖN ÄSCII}    3

Invalid key
    [Template]    NONE
    Variable Should Not Exist    ${NON HASHABLE KEY}

Non-dict cannot be used as dict variable 1
    [Template]    NONE
    Variable Should Not Exist    ${NON DICT DICT 1}

Non-dict cannot be used as dict variable 2
    [Template]    NONE
    Variable Should Not Exist    ${NON DICT DICT 2}

Non-dict cannot be used as dict variable 3
    [Template]    NONE
    Variable Should Not Exist    ${NON DICT DICT 3}

*** Keywords ***
Dict Variable Should Be Equal
    [Arguments]    ${dict}    ${expected}
    ${expected} =    Evaluate    ${expected}
    Dictionaries Should Be Equal    ${dict}    ${expected}
