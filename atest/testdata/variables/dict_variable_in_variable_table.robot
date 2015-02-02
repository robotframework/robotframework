*** Settings ***
Library               Collections
Test Template         Dict Variable Should Be Equal

*** Variables ***
&{FIRST DICT EVER}    key=value    foo=bar
&{EMPTY DICT}
&{EQUALS}             key=value with=sign        empty value=    =    ===
&{ESCAPING EQUALS}    esc\=key=esc\=value    bs\\=\\    bs\\\=\\=    \===
&{NO EQUAL}           haz equal=here    but not here
&{VARIABLES}          a=${1}    ${2}=b    ${True}=${False}
@{LIST}               ${1}    ${2}    ${3}
&{LIST VALUES}        scalar=${LIST}    list=@{LIST}
&{DICT VALUES}        scalar=${FIRST DICT EVER}    dict=&{EMPTY DICT}
&{INVALID KEY}        ${LIST}=doesn't work
&{NON DICT AS DICT}   name=&{LIST}

*** Test Cases ***
Dict variable
    ${FIRST DICT EVER}    {'key': 'value', 'foo': 'bar'}
    ${EMPTY DICT}         {}

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

Invalid key
    [Template]    NONE
    Variable Should Not Exist    ${INVALID KEY}

Non-dict cannot be used as dict variable
    [Template]    NONE
    Variable Should Not Exist    ${NON DICT AS DICT}


*** Keywords ***
Dict Variable Should Be Equal
    [Arguments]    ${dict}    ${expected}
    ${expected} =    Evaluate    ${expected}
    Dictionaries Should Be Equal    ${dict}    ${expected}
