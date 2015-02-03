*** Settings ***
Library               Collections
Test Template         Dict Variable Should Be Equal

*** Variables ***
&{FIRST DICT EVER}    key=value    foo=bar
&{EMPTY DICT}
&{NÖN ÄSCII}          nön=äscii    snowman=\u2603
&{SPACES}             \ lead=    =trail \    \ \ 2 \ = \ \ 3 \ \ \
&{EQUALS}             key=value with=sign        empty value=    =    ===
&{ESCAPING EQUALS}    esc\=key=esc\=value    bs\\=\\    bs\\\=\\=    \===
&{NO EQUAL}           haz equal=here    but not here
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
&{INVALID KEY}        ${LIST}=doesn't work
&{NON DICT DICT 1}    name=&{LIST}
&{NON DICT DICT 2}    &{SPACE}
&{NON DICT DICT 3}    &{EMPTY DICT.keys()}

*** Test Cases ***
Dict variable
    ${FIRST DICT EVER}    {'key': 'value', 'foo': 'bar'}
    ${EMPTY DICT}         {}
    ${NÖN ÄSCII}          {u'nön': u'äscii', 'snowman': u'\\u2603'}
    ${SPACES}             {' lead': '', '': 'trail ', ' \ 2 \ ': ' \ \ 3 \ \ '}

First non-escaped equal sign is separator
    ${EQUALS}             {'key': 'value with=sign', 'empty value': '', '': '', '': '=='}
    ${ESCAPING EQUALS}    {'esc=key': 'esc=value', 'bs\\\\': '\\\\', 'bs\\\\=\\\\': '', '=': '='}

Dict items must contain equal sign
    [Template]    NONE
    Variable Should Not Exist    ${NO EQUAL}

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

Items from dict variable
    ${USE DICT}           {'key': 'value', 'foo': 'that', 'new': 'this'}
    ${USE DICT EXTENDED}  {'key': 'value', 'foo': None, 'new': None}
    ${USE DICT INTERNAL}  {'key': 'value', 'foo': 42, 'new': 42}

Invalid key
    [Template]    NONE
    Variable Should Not Exist    ${INVALID KEY}

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
