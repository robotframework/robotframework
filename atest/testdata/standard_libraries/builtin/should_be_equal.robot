*** Settings ***
Variables         variables_to_verify.py

*** Test Cases ***
Should Be Equal
    [Documentation]    FAIL Error message: A != B
    [Template]    Should Be Equal
    Hello!                        Hello!
    ${1.0}                        ${1}
    ${BYTES WITHOUT NON ASCII}    ${BYTES WITHOUT NON ASCII}
    A                             B    Error message    values=yes

Should Be Equal case-insensitive
    [Documentation]    FAIL yötä != päivää
    [Template]    Should Be Equal
    test value      TEST VALUE      ignore_case=True
    HYVÄÄ YÖTÄ      hyvää yötä      ignore_case=yes
    ${42}           ${42}           ignore_case=True
    Yötä            Päivää          ignore_case=yep!

Should Be Equal fails with values
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 3: 1 != 2
    ...
    ...    2) c: a != b
    ...
    ...    3) z: x != y
    [Template]    Should Be Equal
    1    2    3
    a    b    c    values=true
    x    y    z    values=${42}

Should Be Equal fails without values
    [Documentation]    FAIL Several failures occurred:\n\n 1) 3\n\n 2) c\n\n 3) z\n\n 4) -
    [Template]    Should Be Equal
    1    2    3    values=FALSE
    a    b    c    No Values
    x    y    z    values=no
    .    ,    -    ${NONE}

Should Be Equal with multiline text uses diff
    [Documentation]    FAIL
    ...    Multiline strings are different:
    ...    --- first
    ...    +++ second
    ...    @@ -1,3 +1,4 @@
    ...    \ foo
    ...    \ bar
    ...    +gar
    ...    \ dar\n
    Should Be Equal    foo\nbar\ndar    foo\nbar\ngar\ndar

Should Be Equal with multiline diff text requires both multiline
    [Documentation]    FAIL foo\nbar\ndar != foobar
    Should Be Equal    foo\nbar\ndar    foobar

Should Be Equal with multiline text will not use diff if values are not included
    [Documentation]    FAIL Custom message
    Should Be Equal    foo\nbar\ndar    foo\nbar\ngar\ndar   Custom message    values=FALSE

Should Be Equal tuple and list with same items fails
    [Documentation]    FAIL not same
    Should Be Equal    ${TUPLE 1}    ${LIST 1}    not same    values=false

Should Be Equal dictionaries of different type with same items passes
    Should Be Equal    ${DICT}    ${ORDERED DICT}
    Should Be True    $DICT == dict($ORDERED_DICT)    Sanity check

Should Be Equal with bytes containing non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} != ${BYTES WITHOUT NON ASCII}
    Should Be Equal    ${BYTES WITH NON ASCII}    ${BYTES WITH NON ASCII}
    Should Be Equal    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}

Should Be Equal with unicode and bytes with non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} != this fails
    Should Be Equal    ${BYTES WITH NON ASCII}    this fails

Should Be Equal when types differ but string representations are same
    [Documentation]    FAIL 1 (string) != 1 (integer)
    Should Be Equal    1    ${1}

Should Not Be Equal
    [Documentation]    FAIL foo == foo
    [Template]    Should Not Be Equal
    foo    bar
    1      ${1}
    foo    foo

Should Not Be Equal case-insensitive
    [Documentation]     FAIL foo == foo
    [Template]  Should Not Be Equal
    test value      TEST VALUE1     ignore_case=True
    HYVÄÄ YÖTÄ      hyvää yötä1     ignore_case=True
    foo             FOO             ignore_case=True

Should Not Be Equal with bytes containing non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} == ${BYTES WITH NON ASCII}
    Should Not Be Equal    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}
    Should Not Be Equal    ${BYTES WITH NON ASCII}    unicode
    Should Not Be Equal    ${BYTES WITH NON ASCII}    ${BYTES WITH NON ASCII}
