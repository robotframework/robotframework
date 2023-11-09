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
    Straße      ss     ignore_case=true
    ${LIST}     CEE    ignore_case=!!!
    ${DICT}     Ä      ignore_case=yes
    ${DICT1}    XXX    ignore_case=yes

Should Contain without leading spaces
    [Documentation]    FAIL '${DICT4}' does not contain '\na'
    [Template]    Should Contain
    abcdefg     \n\tcd     strip_spaces=leading
    \t HYVÄ     VÄ         strip_spaces=Leading
    \n bar      \tba       strip_spaces=leadinG
    ${DICT4}    \ a        strip_spaces=LEADING
    ${DICT4}    \n a b     strip_spaces=leading
    ${DICT4}    c          strip_spaces=leading
    ${DICT4}    \na        strip_spaces=NO

Should Contain without trailing spaces
    [Documentation]    FAIL  '${DICT4}' does not contain 'a'
    [Template]    Should Contain
    abcdefg     cd\n\t     strip_spaces=trailing
    HYVÄ \t     VÄ         strip_spaces=Trailing
    bar \n      ba\t       strip_spaces=TRAILING
    ${DICT4}    a\t        strip_spaces=trailinG
    ${DICT4}    a b\t\n    strip_spaces=trailing
    ${DICT4}    dd \t      strip_spaces=trailing

Should Contain without leading and trailing spaces
    [Documentation]    FAIL '${DICT4}' does not contain '\ dd\t'
    [Template]    Should Contain
    abcdefg      \tcd\n    strip_spaces=True
    \n HYVÄ\t    VÄ        strip_spaces=TRUE
    \ bar \n     \ ba\t    strip_spaces=yes
    ${DICT4}     \na\t     strip_spaces=TRUE
    ${DICT4}     \ta b\n   strip_spaces=Yes
    ${DICT4}     \ ak\n    strip_spaces=True
    ${DICT4}     \ dd\t    strip_spaces=no

Should Contain and do not collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'ab\n\tefg' does not contain '\tcd\n'
    ...
    ...    2) '\n HYV Ä\t' does not contain 'VÄ'
    ...
    ...    3) '${DICT_4}' does not contain 'a\tb\n'
    ...
    ...    4) '${LIST_4}' does not contain '\t\tc\n'
    [Template]    Should Contain
    ab\n\tefg     \tcd\n     collapse_spaces=False
    \n HYV Ä\t    VÄ         collapse_spaces=${FALSE}
    \ bar \n      \ ba       collapse_spaces=0
    ${DICT4}      a\tb\n     collapse_spaces=No
    ${LIST4}      \t\tc\n    collapse_spaces=FALSE

Should Contain and collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'ab\n\tefg' does not contain ' cd '
    ...
    ...    2) '\n HYV Ä\t' does not contain 'VÄ'
    ...
    ...    3) '${DICT_4}' does not contain 'a b '
    ...
    ...    4) '${LIST_4}' does not contain ' b '
    [Template]    Should Contain
    ab\n\tefg     \tcd\n    collapse_spaces=True
    \n HYV Ä\t    VÄ        collapse_spaces=${TRUE}
    b ar          b\n\ta    collapse_spaces=Yes
    ${DICT4}      a\tb\n    collapse_spaces=YES
    ${LIST4}      \tb\n     collapse_spaces=TRUE
    ${LIST4}      \tc\n     collapse_spaces=TRUE

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

Should Not Contain without leading spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'abcdefg' contains 'cd'
    ...
    ...    2) '\nHYVÄ' contains 'VÄ'
    ...
    ...    3) '${DICT_4}' contains 'a'
    [Template]    Should Not Contain
    abcdefg      \ncd         strip_spaces=leading
    \nHYVÄ       \tVÄ         strip_spaces=Leading
    ${DICT}      \nÅ          strip_spaces=LEADING
    ${DICT_4}    ${SPACE}a    strip_spaces=leading

Should Not Contain without trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'abcdefg' contains 'cd'
    ...
    ...    2) 'HYVÄ\n' contains 'VÄ'
    ...
    ...    3) '${DICT_4}' contains 'dd'
    [Template]    Should Not Contain
    abcdefg      cd\n          strip_spaces=trailing
    HYVÄ\n       VÄ\t          strip_spaces=Trailing
    ${DICT}      Å\n           strip_spaces=TRAILING
    ${DICT_4}    dd${SPACE}    strip_spaces=trailing

Should Not Contain without leading and trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) '\nabcdefg' contains 'cd'
    ...
    ...    2) 'HYVÄ\n' contains 'VÄ'
    ...
    ...    3) '${DICT_4}' contains 'a b'
    ...
    ...    4) '${DICT_4}' contains 'dd\n\t'
    [Template]    Should Not Contain
    \nabcdefg    cd\n         strip_spaces=True
    HYVÄ\n       \tVÄ         strip_spaces=true
    ${DICT_4}    \na b\t      strip_spaces=YES
    ${DICT_4}    dd\n\t       strip_spaces=No

Should Not Contain and do not collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'ab\tcdefg' contains '\tcd'
    ...
    ...    2) 'HY \ \ VÄ\t' contains 'VÄ'
    ...
    ...    3) '${DICT_4}' contains '\ta'
    ...
    ...    4) '${LIST_4}' contains '\tc\n'
    [Template]    Should Not Contain
    ab\tcdefg      \tcd     collapse_spaces=False
    HY \ \ VÄ\t    VÄ       collapse_spaces=FALSE
    ${DICT4}       \ta      collapse_spaces=${FALSE}
    ${LIST4}       \tc\n    collapse_spaces=No

Should Not Contain and collapse spaces
        [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'ab\tcdefg' contains 'cd'
    ...
    ...    2) 'HY\tVÄ\t' contains 'VÄ'
    ...
    ...    3) '${DICT_4}' contains 'a b'
    ...
    ...    4) '${LIST_4}' contains ' a'
    ...
    ...    5) '${LIST_4}' contains 'b '
    [Template]    Should Not Contain
    ab\tcdefg    cd      collapse_spaces=TRUE
    HY\tVÄ\t     VÄ      collapse_spaces=True
    ${DICT4}     a\tb    collapse_spaces=${TRUE}
    ${LIST4}     \ a     collapse_spaces=Yes
    ${LIST4}     b\t     collapse_spaces=TRue
