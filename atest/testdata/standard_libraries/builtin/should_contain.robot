*** Settings ***
Variables         variables_to_verify.py

*** Test Cases ***
Should Contain
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) The Message: 'abcdefg' does not contain 'ABCDEFG'
    ...
    ...    2) Message
    [Template]    Should Contain
    abcdefg    cd
    abcdefg    abcdefg    This succeeds
    abcdefg    ABCDEFG    The Message
    abcdefg    x          Message    values=false

Should Contain with non-strings
    [Documentation]    FAIL '['a', 2]' does not contain '3'
    [Template]    Should Contain
    ${LIST1}     a
    ${TUPLE2}    ${2}
    ${DICT}      ä
    ${DICT2}     ${2}
    ${LIST2}     ${3}

Should Contain case-insensitive
    [Documentation]    FAIL '{'a': 1}' does not contain 'xxx'
    [Template]    Should Contain
    abcdefg     CD     ignore_case=True
    HYVÄ        vä     ignore_case=yes
    ${LIST}     CEE    ignore_case=!!!
    ${DICT}     Ä      ignore_case=yes
    ${DICT1}    XXX    ignore_case=yes

Should Not Contain
    [Documentation]    FAIL 'Hello yet again' contains 'yet'
    [Template]    Should Not Contain
    Hello again    yet
    Hello yet again    yet

Should Not Contain with non-strings
    [Documentation]    FAIL '['a', 2]' contains '2'
    [Template]    Should Not Contain
    ${LIST}     xxx
    ${DICT}     ${42}
    ${LIST2}    ${2}

Should Not Contain case-insensitive
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'abcdefg' contains 'cd'
    ...
    ...    2) 'HYVÄ' contains 'vä'
    ...
    ...    3) '{'a': 1}' contains 'a'
    [Template]    Should Not Contain
    abcdefg     CD    ignore_case=True
    HYVÄ        vä    ignore_case=yes
    ${DICT}     Å     ignore_case=yes
    ${DICT1}    A     ignore_case=yes


