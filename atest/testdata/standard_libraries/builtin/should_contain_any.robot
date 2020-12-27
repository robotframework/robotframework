*** Settings ***
Variables         variables_to_verify.py

*** Test Cases ***
Should Contain Any
    [Template]    Should Contain Any
    abcdefg    c
    åäö        x    y    z    ä    b
    ${LIST}    x    y    z    e    b    c
    ${DICT}    x    y    z    a    b    c
    ${LIST}    41    ${42}    43

Should Contain Any failing
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Message
    ...
    ...    2) Message: 'abcdefg' does not contain any of 'x'
    ...
    ...    3) 'abcdefg' does not contain any of 'x'
    ...
    ...    4) 'abcdefg' does not contain any of 'x' or 'y'
    ...
    ...    5) Message: 'abcdefg' does not contain any of 'x', 'y' or 'Ф'
    [Template]    Should Contain Any
    abcdefg    x    msg=Message    values=False
    abcdefg    x    msg=Message
    abcdefg    x
    abcdefg    x    y
    abcdefg    x    y    Ф    msg=Message

Should Contain Any case-insensitive
    [Documentation]    FAIL    Fails: '{'a': 1}' does not contain any of 'x'
    [Template]    Should Contain Any
    Hyvä         vÄ             ignore_case=True
    ${LIST}      ${-1}    B     ignore_case=yes
    ${LIST}      41    ${42}    ignore_case=True
    ${DICT 1}    x              ignore_case=True    msg=Fails

Should Contain Any without leading spaces
    [Documentation]    FAIL    '${DICT_1}' does not contain any of 'x'
    [Template]    Should Contain Any
    Hyvä           \nvä              strip_spaces=leading
    \tSan Diego    \ San             strip_spaces=leading
    ${LIST}        ${-1}    \tb      strip_spaces=Leading
    ${LIST}        41       \tcee    strip_spaces=LEADING
    ${DICT 1}      \tx               strip_spaces=leading
    ${DICT_4}      \tc      \ g      strip_spaces=leading

Should Contain Any without trailing spaces
    [Documentation]    FAIL    '${DICT_1}' does not contain any of 'x'
    [Template]    Should Contain Any
    Hyvä           vä\n              strip_spaces=trailing
    San Diego\n    Diego             strip_spaces=Trailing
    ${LIST}        ${-1}    b\t      strip_spaces=TRAILING
    ${LIST}        41       cee\t    strip_spaces=trailing
    ${DICT 1}      x\t               strip_spaces=trailing
    ${DICT_4}      dd\t     g\t      strip_spaces=trailing

Should Contain Any without leading and trailing spaces
    [Documentation]    FAIL    '${DICT_1}' does not contain any of '\ x\t'
    [Template]    Should Contain Any
    Hyvä             \tvä\n                 strip_spaces=True
    \ San Diego\n    Diego                  strip_spaces=TRUE
    ${LIST}          ${-1}     \ b\t        strip_spaces=Yes
    ${LIST}          41        \t\tcee\t    strip_spaces=1
    ${DICT 1}        \ x\t                  strip_spaces=No
    ${DICT_4}        \tak\t    g\t          strip_spaces=Sure

Should Contain Any without items fails
    [Documentation]    FAIL    One or more items required.
    Should Contain Any    foo

Should Contain Any with invalid configuration
    [Documentation]    FAIL    Unsupported configuration parameters: 'bad parameter' and 'шта'.
    Should Contain Any    abcdefg    +    \=    msg=Message    bad parameter=True    шта=?

Should Not Contain Any
    [Template]    Should Not Contain Any
    abcdefg    x
    abcdefg    x    y    z
    ${LIST}    x    y    z    ${1}
    ${DICT}    x    y    z    ${1}

Should Not Contain Any failing
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Message
    ...
    ...    2) Message: 'abcdefg' contains one or more of 'b'
    ...
    ...    3) 'abcdefg' contains one or more of 'c'
    ...
    ...    4) 'abcdefg' contains one or more of 'x' or 'd'
    ...
    ...    5) Message: 'abcdefg' contains one or more of 'x', 'y', 'Ф' or 'e'
    [Template]    Should Not Contain Any
    abcdefg    a    msg=Message    values=False
    abcdefg    b    msg=Message
    abcdefg    c
    abcdefg    x    d
    abcdefg    x    y    Ф    e    msg=Message

Should Not Contain Any case-insensitive
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'abcdefg' contains one or more of 'a'
    ...
    ...    2) 'ABCDEFG' contains one or more of 'abc'
    ...
    ...    3) '['a', 'b', 'cee', 'b', 42]' contains one or more of '1' or 'b'
    ...
    ...    4) '{'a': 1}' contains one or more of 'a'
    [Template]    Should Not Contain Any
    abcdefg      x            ignore_case=True    msg=This succeeds
    abcdefg      A            ignore_case=True
    ABCDEFG      abc          ignore_case=True
    ${LIST}      ${1}    B    ignore_case=True
    ${DICT 1}    A            ignore_case=True

Should Not Contain Any without leading spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'abcd\tx' contains one or more of 'x'
    ...
    ...    2) '${DICT_4}' contains one or more of 'a'
    [Template]    Should Not Contain Any
    abcd\tx      \tx      strip_spaces=leading
    ${DICT_4}    \n\ta    strip_spaces=LEADING

Should Not Contain Any without trailing spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'abcx\td' contains one or more of 'x'
    ...
    ...    2) '${DICT_4}' contains one or more of 'dd'
    [Template]    Should Not Contain Any
    abcx\td      x\t       strip_spaces=trailing
    ${DICT_4}    dd\n\n    strip_spaces=TRAILING

Should Not Contain Any without leading and trailing spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'abcx\td' contains one or more of 'x'
    ...
    ...    2) '${DICT_4}' contains one or more of 'dd'
    ...
    ...    3) '${DICT_4}' contains one or more of 'ak'
    ...
    ...    4) '${DICT_4}' contains one or more of 'a'
    [Template]    Should Not Contain Any
    abcx\td      \ x\t       strip_spaces=True
    ${DICT_4}    \tdd\n      strip_spaces=${True}
    ${DICT_4}    \ ak\t\t    strip_spaces=TRUE
    ${DICT_4}    \ a\t\t     strip_spaces=Yes

Should Not Contain Any without items fails
    [Documentation]    FAIL    One or more items required.
    Should Not Contain Any    foo

Should Not Contain Any with invalid configuration
    [Documentation]    FAIL    Unsupported configuration parameter: 'bad parameter'.
    Should Not Contain Any    abcdefg    +    \=    msg=Message    bad parameter=True
