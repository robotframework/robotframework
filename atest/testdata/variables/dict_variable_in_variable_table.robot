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
&{DICT VALUES}        scalar=${FIRST DICT EVER}    dict=&{EMPTY DICT}
&{OVERRIDE}           a=1    a=2    b=1    a=3    b=2    b=3    a=4    a=5
&{OVERRIDE W/ VARS}   ${1}=a    ${1.0}=b    ${0+1}=c    ${1*1}=d    ${1.00}=e    ${1+0}=f
&{USE DICT}           key=not    &{FIRST DICT EVER}    &{EMPTY DICT}    new=this    foo=that
&{INVALID KEY}        ${LIST}=doesn't work
&{NON DICT DICT 1}    name=&{LIST}
&{NON DICT DICT 2}    &{SPACE}

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
    ${DICT VALUES}        {'scalar': {'key': 'value', 'foo': 'bar'}, 'dict': {}}

Last item overrides
    ${OVERRIDE}           {'a': '5', 'b': '3'}
    ${OVERRIDE W/ VARS}   {1: 'f'}

Items from dict variable
    ${USE DICT}           {'key': 'value', 'foo': 'that', 'new': 'this'}

Invalid key
    [Template]    NONE
    Variable Should Not Exist    ${INVALID KEY}

Non-dict cannot be used as dict variable 1
    [Template]    NONE
    Variable Should Not Exist    ${NON DICT DICT 1}

Non-dict cannot be used as dict variable 2
    [Template]    NONE
    Variable Should Not Exist    ${NON DICT DICT 2}

*** Keywords ***
Dict Variable Should Be Equal
    [Arguments]    ${dict}    ${expected}
    ${expected} =    Evaluate    ${expected}
    Dictionaries Should Be Equal    ${dict}    ${expected}
