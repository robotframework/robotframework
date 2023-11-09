*** Settings ***
Test Template     Should Be Equal
Variables         variables_to_verify.py

*** Test Cases ***
Basics
    [Documentation]    FAIL Error message: A != B
    Hello!                        Hello!
    Multi\nline\ntext\n\n!!!\n    Multi\nline\ntext\n\n!!!\n
    ${1.0}                        ${1}
    ${BYTES WITHOUT NON ASCII}    ${BYTES WITHOUT NON ASCII}    repr=True
    A                             B    Error message    values=yes

Case-insensitive
    [Documentation]    FAIL yötä != päivää
    test value      TEST VALUE      ignore_case=True
    HYVÄÄ YÖTÄ      hyvää yötä      repr=True    ignore_case=yes
    Straße          strasse         ignore_case=True
    ${42}           ${42}           ignore_case=True
    Yötä            Päivää          ignore_case=yep!

Without leading spaces
    [Documentation]    FAIL test != value
    ${SPACE}test    test            strip_spaces=leading
    hyvää yötä      \nhyvää yötä    repr=True    strip_spaces=Leading
    \t${42}         \t${42}         strip_spaces=LEADING
    \ntest          \n value        strip_spaces=leading

Without trailing spaces
    [Documentation]    FAIL test != value
    test${SPACE}    test            strip_spaces=trailing
    hyvää yötä      hyvää yötä\t    repr=True    strip_spaces=Trailing
    ${42}\t         ${42}\n         strip_spaces=TRAILING
    test\n          value\t         strip_spaces=trailing

Without leading and trailing spaces
    [Documentation]    FAIL test != value
    test${SPACE}       test               strip_spaces=True
    hyvää yötä         hyvää yötä\t       repr=True    strip_spaces=TRUE
    ${SPACE}${42}\n    ${SPACE}${42}\t    strip_spaces=yeS
    \n\ test\t         ${SPACE}value\n    strip_spaces=yes

Do not collapse spaces
    [Documentation]    FAIL repr=True: Yö \ntä != Yö\ttä
    ${SPACE * 5}test${SPACE * 2}value    ${SPACE * 5}test${SPACE * 2}value    collapse_spaces=False
    HYVÄÄ\tYÖTÄ${SPACE * 3}              HYVÄÄ\tYÖTÄ${SPACE * 3}              repr=True    collapse_spaces=False
    ${42}                                ${42}                                collapse_spaces=${FALSE}
    Yö \ntä                              Yö\ttä                               repr=True    collapse_spaces=False

Collapse spaces
    [Documentation]    FAIL Yo yo != Oy oy
    test${SPACE * 4}value${SPACE * 5}    test value${SPACE}    collapse_spaces=True
    ${SPACE * 5}HYVÄÄ\t\nYÖTÄ            ${SPACE}HYVÄÄ YÖTÄ    repr=True    collapse_spaces=Yes
    ${42}                                ${42}                 collapse_spaces=${TRUE}
    Yo${SPACE * 5}yo                     Oy\toy                collapse_spaces=True

Fails with values
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 3: 1 != 2
    ...
    ...    2) c: a != b
    ...
    ...    3) z: x != y
    1    2    3
    a    b    c    values=true
    x    y    z    values=${42}

Fails without values
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 3
    ...
    ...    2) c
    ...
    ...    3) z
    ...
    ...    4) -
    1    2    3    values=FALSE
    a    b    c    No Values
    x    y    z    values=no
    .    ,    -    ${NONE}

Multiline comparison uses diff
    [Documentation]    FAIL
    ...    Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,6 @@
    ...     foo
    ...     bar
    ...    +gar
    ...    +
    ...     dar
    ...    +
    foo\nbar\ndar\n    foo\nbar\ngar\n\ndar\n\n

Multiline comparison with custom message
    [Documentation]    FAIL
    ...    Custom message of mine: Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,6 @@
    ...     foo
    ...     bar
    ...    +gar
    ...    +
    ...     dar
    ...    +
    foo\nbar\ndar\n    foo\nbar\ngar\n\ndar\n\n    msg=Custom message of mine

Multiline comparison requires both multiline
    [Documentation]    FAIL foo\nbar\ndar != foobar
    foo\nbar\ndar    foobar

Multiline comparison without including values
    [Documentation]    FAIL Custom message
    foo\nbar\ndar    foo\nbar\ngar\ndar   Custom message    values=FALSE

formatter=repr
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'foo' != 'bar'
    ...
    ...    2) NB != NB
    ...
    ...    3) 'NB' != 'NB\\x00'
    ...
    ...    4) NL != NL
    ...
    ...
    ...    5) 'NL' != 'NL\\r\\n'
    ...
    ...    6) ('a',) != ('a', 2)
    foo          bar          formatter=repr
    NB           NB\x00       formatter=str
    NB           NB\x00       formatter=REPR
    NL           NL\r\n       formatter=STR
    NL           NL\r\n       formatter=Repr
    ${TUPLE1}    ${TUPLE2}    formatter=repr

formatter=repr/ascii with non-ASCII characters
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) Ä != A
    ...
    ...    2) 'Ä' != 'A'
    ...
    ...    3) '\\xc4' != 'A'
    ...
    ...    4) Ä (string) != Ä (string)
    ...
    ...    5) 'Ä' (string) != 'Ä' (string)
    ...
    ...    6) '\\xc4' != 'A\\u0308'
    ...
    ...    7) {'a': 1, 'A': 2, 'ä': 3, 'Ä': 4} != {'a': 1}
    ...
    ...    8) ${ASCII DICT} != {'a': 1}
    Ä          A
    Ä          A           formatter=repr
    Ä          A           formatter=ascii
    Ä          A\u0308     formatter=str
    Ä          A\u0308     formatter=Repr
    Ä          A\u0308     formatter=ASCII
    ${DICT}    ${DICT1}    formatter=repr
    ${DICT}    ${DICT1}    formatter=ascii

formatter=repr with multiline
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,6 @@
    ...     foo
    ...     bar
    ...    +gar
    ...    +
    ...     dar
    ...    +
    ...
    ...    2) Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,6 @@
    ...     'foo\\n'
    ...     'bar\\n'
    ...    +'gar\\n'
    ...    +'\\n'
    ...     'dar\\n'
    ...    +'\\n'
    foo\nbar\ndar\n    foo\nbar\ngar\n\ndar\n\n
    foo\nbar\ndar\n    foo\nbar\ngar\n\ndar\n\n   formatter=repr

formatter=repr with multiline and different line endings
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,3 @@
    ...    -1
    ...    -2
    ...    -3
    ...    +1
    ...    +2
    ...    +3
    ...
    ...    2) Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,3 @@
    ...    -'1\\r\\n'
    ...    -'2\\r\\n'
    ...    -'3'
    ...    +'1\\n'
    ...    +'2\\n'
    ...    +'3\\n'
    1\r\n2\r\n3    1\n2\n3\n    formatter=str
    1\r\n2\r\n3    1\n2\n3\n    formatter=REPR

formatter=repr/ascii with multiline and non-ASCII characters
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,3 @@
    ...     Å
    ...    -Ä
    ...    +Ä
    ...     Ö
    ...
    ...    2) Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,3 @@
    ...     'Å\\n'
    ...    -'Ä\\n'
    ...    +'Ä\\n'
    ...     'Ö\\n'
    ...
    ...    3) Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,3 @@
    ...     '\\xc5\\n'
    ...    -'\\xc4\\n'
    ...    +'A\\u0308\\n'
    ...     '\\xd6\\n'
    Å\nÄ\n\Ö\n    Å\nA\u0308\n\Ö\n
    Å\nÄ\n\Ö\n    Å\nA\u0308\n\Ö\n    formatter=repr
    Å\nÄ\n\Ö\n    Å\nA\u0308\n\Ö\n    formatter=ascii

Invalid formatter
    [Documentation]    FAIL ValueError: Invalid formatter 'invalid'. Available 'str', 'repr', 'ascii', 'len', and 'type'.
    1    1    formatter=invalid

Tuple and list with same items fail
    [Documentation]    FAIL not same
    ${TUPLE 1}    ${LIST 1}    not same    values=false

Dictionaries of different type with same items pass
    ${DICT}    ${ORDERED DICT}
    [Teardown]    Should Be True    $DICT == dict($ORDERED_DICT)    Sanity check

Bytes containing non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} != ${BYTES WITHOUT NON ASCII}
    ${BYTES WITH NON ASCII}    ${BYTES WITH NON ASCII}
    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}

Unicode and bytes with non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} != this fails
    ${BYTES WITH NON ASCII}    this fails

Types info is added if string representations are same
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 1 (string) != 1 (integer)
    ...
    ...    2) True (boolean) != True (string)
    1          ${1}
    ${True}    True

Should Not Be Equal
    [Documentation]    FAIL foo == foo
    [Template]    Should Not Be Equal
    foo    bar
    1      ${1}
    foo    foo

Should Not Be Equal case-insensitive
    [Documentation]     FAIL fööss == fööss
    [Template]  Should Not Be Equal
    test value      TEST VALUE1     ignore_case=True
    HYVÄÄ YÖTÄ      hyvää yötä1     ignore_case=True
    ${42}           ${43}           ignore_case=True
    fööß            FÖÖSS           ignore_case=True

Should Not Be Equal without leading spaces
    [Documentation]     FAIL Several failures occurred:
    ...
    ...    1) test == test
    ...
    ...    2) hyvää yötä == hyvää yötä
    ...
    ...    3) 42 == 42
    [Template]  Should Not Be Equal
    ${SPACE}test    test            strip_spaces=leading
    hyvää yötä      \nhyvää yötä    strip_spaces=Leading
    ${42}           ${42}           strip_spaces=LEADING
    \t\ntest        \n\tvalue       strip_spaces=leading

Should Not Be Equal without trailing spaces
    [Documentation]     FAIL Several failures occurred:
    ...
    ...    1) test == test
    ...
    ...    2) hyvää yötä == hyvää yötä
    ...
    ...    3) 42 == 42
    [Template]  Should Not Be Equal
    test${SPACE}    test            strip_spaces=trailing
    hyvää yötä      hyvää yötä\t    strip_spaces=Trailing
    ${42}           ${42}           strip_spaces=TRAILING
    test\t\n        value \n        strip_spaces=TraIling

Should Not Be Equal without leading and trailing spaces
    [Documentation]     FAIL Several failures occurred:
    ...
    ...    1) test == test
    ...
    ...    2) hyvää yötä == hyvää yötä
    ...
    ...    3) 42 == 42
    [Template]  Should Not Be Equal
    test${SPACE}    test            strip_spaces=True
    hyvää yötä      hyvää yötä\t    strip_spaces=TRUE
    \ test\t\n      \tvalue\t       strip_spaces=yeS
    ${42}           ${42}           strip_spaces=This probably should be an error.

Should Not Be Equal and do not collapse spaces
    [Documentation]     FAIL Several failures occurred:
    ...
    ...    1) test\tit == test\tit
    ...
    ...    2) repr=True: hyvää\ \nyötä == hyvää\ \nyötä
    ...
    ...    3) \ \ 42 == \ \ 42
    [Template]  Should Not Be Equal
    test\tit         test\tit         collapse_spaces=No
    hyvää\ \nyötä    hyvää\ \nyötä    repr=True    collapse_spaces=${FALSE}
    \ test\t\nit     \tvalue\tit      collapse_spaces=${NONE}
    \ \ ${42}        \ \ ${42}        collapse_spaces=False

Should Not Be Equal and collapse spaces
    [Documentation]     FAIL Several failures occurred:
    ...
    ...    1) test it == test it
    ...
    ...    2) repr=True: hyvää yötä == hyvää yötä
    ...
    ...    3) \ 42 == \ 42
    [Template]  Should Not Be Equal
    test\t\nit       test\ \tit       collapse_spaces=True
    hyvää\ \ yötä    hyvää\ \ yötä    repr=True    collapse_spaces=${TRUE}
    \ test\tit       \tvalue it       collapse_spaces=Maybe yes
    \ \ ${42}        \ \ ${42}        collapse_spaces=TruE

Should Not Be Equal with bytes containing non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} == ${BYTES WITH NON ASCII}
    [Template]  Should Not Be Equal
    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}
    ${BYTES WITH NON ASCII}    unicode
    ${BYTES WITH NON ASCII}    ${BYTES WITH NON ASCII}
