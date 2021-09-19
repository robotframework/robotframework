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
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) '${DICT 1}' does not contain any of 'x'
    ...
    ...    2) '${DICT 5}' does not contain any of 'b\t'
    [Template]    Should Contain Any
    Hyvä           \nvä              strip_spaces=leading
    \tSan Diego    \ San             strip_spaces=leading
    ${LIST}        ${-1}    \tb      strip_spaces=Leading
    ${LIST}        41       \tcee    strip_spaces=LEADING
    ${DICT 1}      \tx               strip_spaces=leading
    ${DICT 4}      \tc      \ g      strip_spaces=leading
    ${DICT 5}      \tb               strip_spaces=leading
    ${DICT 5}      b\t               strip_spaces=leading

Should Contain Any without trailing spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) '${DICT 1}' does not contain any of 'x'
    ...
    ...    2) '${DICT 5}' does not contain any of '\nd'
    [Template]    Should Contain Any
    Hyvä           vä\n              strip_spaces=trailing
    San Diego\n    Diego             strip_spaces=Trailing
    ${LIST}        ${-1}    b\t      strip_spaces=TRAILING
    ${LIST}        41       cee\t    strip_spaces=trailing
    ${DICT 1}      x\t               strip_spaces=trailing
    ${DICT 4}      dd\t     g\t      strip_spaces=trailing
    ${DICT 5}      d\n               strip_spaces=trailing
    ${DICT 5}      \nd               strip_spaces=trailing

Should Contain Any without leading and trailing spaces
    [Documentation]    FAIL    '${DICT 1}' does not contain any of '\ x\t'
    [Template]    Should Contain Any
    Hyvä             \tvä\n                 strip_spaces=True
    \ San Diego\n    Diego                  strip_spaces=TRUE
    ${LIST}          ${-1}     \ b\t        strip_spaces=Yes
    ${LIST}          41        \t\tcee\t    strip_spaces=1
    ${DICT 1}        \ x\t                  strip_spaces=No
    ${DICT 4}        \tak\t    g\t          strip_spaces=Sure

Should Contain Any and do not collapse spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'Hyvä' does not contain any of '\tVä\n'
    ...
    ...    2) '\ San\tDiego\n' does not contain any of 'Di ego'
    ...
    ...    3) '${LIST}' does not contain any of '\n\tab' or '\ b\t'
    ...
    ...    4) '${DICT 4}' does not contain any of '\tak' or 'dd\t'
    [Template]    Should Contain Any
    Hyvä              \tVä\n             collapse_spaces=False
    \ San\tDiego\n    Di ego             collapse_spaces=FALSE
    ${LIST}           \n\tab    \ b\t    collapse_spaces=No
    ${DICT 4}         \tak      dd\t     collapse_spaces=${FALSE}

Should Contain Any and collapse spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'Hyvä' does not contain any of ' Vä '
    ...
    ...    2) 'San\tDiego' does not contain any of 'Di ego'
    ...
    ...    3) '${LIST}' does not contain any of ' ab' or ' b '
    ...
    ...    4) '${DICT 4}' does not contain any of ' ak' or 'a b '
    [Template]    Should Contain Any
    Hyvä          \tVä\n                 collapse_spaces=True
    San\tDiego    Di\t\nego              collapse_spaces=TRUE
    ${LIST}       \n\tab       \ b\t     collapse_spaces=Yes
    ${DICT 4}     \tak         a\tb\n    collapse_spaces=${TRUE}
    ${DICT 5}     e e                    collapse_spaces=TRUE
    ${DICT 5}     e \n \t e              collapse_spaces=TRUE

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
    ...    2) '${DICT 4}' contains one or more of 'a'
    [Template]    Should Not Contain Any
    abcd\tx      \tx      strip_spaces=leading
    ${DICT 4}    dd       strip_spaces=leading
    ${DICT 4}    \n\ta    strip_spaces=LEADING

Should Not Contain Any without trailing spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'abcx\td' contains one or more of 'x'
    ...
    ...    2) '${DICT 4}' contains one or more of 'dd'
    [Template]    Should Not Contain Any
    abcx\td      x\t       strip_spaces=trailing
    ${DICT 4}    a         strip_spaces=TRAILING
    ${DICT 4}    dd\n\n    strip_spaces=trailing

Should Not Contain Any without leading and trailing spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'abcx\td' contains one or more of 'x'
    ...
    ...    2) '${DICT 4}' contains one or more of 'dd'
    ...
    ...    3) '${DICT 4}' contains one or more of 'ak'
    ...
    ...    4) '${DICT 4}' contains one or more of 'a'
    [Template]    Should Not Contain Any
    abcx\td      \ x\t       strip_spaces=True
    ${DICT 4}    \tdd\n      strip_spaces=${True}
    ${DICT 4}    \ ak\t\t    strip_spaces=TRUE
    ${DICT 4}    \ a\t\t     strip_spaces=Yes

Should Not Contain Any and do not collapse spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'abc\nx\td' contains one or more of '\nx\t'
    ...
    ...    2) '${DICT 4}' contains one or more of 'dd\n\t'
    ...
    ...    3) '${DICT 4}' contains one or more of '\nak \t'
    ...
    ...    4) '${LIST 4}' contains one or more of '\ta'
    [Template]    Should Not Contain Any
    abc\nx\td    \nx\t      collapse_spaces=False
    ${DICT 4}    dd\n\t     collapse_spaces=${FALSE}
    ${DICT 4}    \nak \t    collapse_spaces=FALSE
    ${LIST 4}    \ta        collapse_spaces=No

Should Not Contain Any and collapse spaces
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'abc x d' contains one or more of ' x '
    ...
    ...    2) '${DICT 4}' contains one or more of 'a b'
    ...
    ...    3) '${DICT 5}' contains one or more of ' a'
    ...
    ...    4) '${LIST 4}' contains one or more of 'b '
    ...
    ...    5) '${DICT 5}' contains one or more of 'e e'
    [Template]    Should Not Contain Any
    abc x d      \nx\t     collapse_spaces=True
    ${DICT 4}    a\t\nb    collapse_spaces=${TRUE}
    ${DICT 5}    \ \ta     collapse_spaces=TRUE
    ${LIST 4}    b\n\t     collapse_spaces=Yes
    ${DICT 5}    e\te       collapse_spaces=TRUE

Should Not Contain Any without items fails
    [Documentation]    FAIL    One or more items required.
    Should Not Contain Any    foo

Should Not Contain Any with invalid configuration
    [Documentation]    FAIL    Unsupported configuration parameter: 'bad parameter'.
    Should Not Contain Any    abcdefg    +    \=    msg=Message    bad parameter=True
