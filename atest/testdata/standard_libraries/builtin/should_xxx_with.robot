*** Variables ***
${LONG}           This is a bit longer sentence and it even has a friend here.
...               This is the friend of the previous sentence and it is also
...               quite long, actually even longer than its friend.

*** Test Cases ***
Should Start With
    [Documentation]    FAIL My message: '${LONG}' does not start with 'Does not start'
    [Template]    Should Start With
    Hello, world!    Hello
    Hello, world!    Hello, world!
    ${LONG}    Does not start    My message    values=true

Should Start With case-insensitive
    [Template]    Should Start With
    Hello!           hELLo            ignore_case=True
    HYVÄÄ YÖTÄ       hyvää            ignore_case=yeah
    Hello, world!    hello, WORLD!    ignore_case=True
    Straße           stras            ignore_case=True

Should Start With without values
    [Documentation]    FAIL My message
    Should Start With    ${LONG}    Nope    My message    values=No values

Should Start With without leading spaces
    [Documentation]    FAIL    'YÖTÄ' does not start with 'yötä'
    [Template]    Should Start With
    ${SPACE}\ttest?    test        strip_spaces=LEADING
    test value         \ttest      strip_spaces=Leading
    \nyötä             \työtä      repr=yes    strip_spaces=leading
    ${SPACE}           ${EMPTY}    strip_spaces=leading
    ${SPACE}YÖTÄ       \nyötä      strip_spaces=leading

Should Start With without trailing spaces
    [Documentation]    FAIL  'YÖTÄ' does not start with 'yötä'
    [Template]    Should Start With
    test\tvalue${SPACE}    test\tvalue       strip_spaces=TRAILING
    test value!            test\t            strip_spaces=Trailing
    yötä\n${SPACE}!        yötä\n            repr=yes    strip_spaces=trailing
    ${SPACE}               ${EMPTY}          strip_spaces=trailing
    YÖTÄ${SPACE}\n         yötä\n${SPACE}    strip_spaces=trailing

Should Start With without leading and trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'test value' does not start with 'test\t'
    ...
    ...    2) 'YÖTÄ' does not start with 'yötä'
    [Template]    Should Start With
    \ttest?${SPACE}    ${SPACE}test\t    strip_spaces=True
    test\ \ value      \ttest\ \ v       strip_spaces=truE
    \nyötä\n\t         yötä\t            repr=yes    strip_spaces=yes
    ${SPACE}           ${EMPTY}          strip_spaces=true
    test value         test\t            strip_spaces=NO
    \t\n\ YÖTÄ\t       \työtä\t\n        strip_spaces=true

Should Start With and do not collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) '\ttest?' does not start with 'test'
    ...
    ...    2) 'test\n\ value' does not start with 'test\ \ v'
    ...
    ...    3) 'YÖTÄ\t' does not start with '\työtä\ntest'
    [Template]    Should Start With
    \ttest?          test            collapse_spaces=False
    test\n\ value    test\ \ v       collapse_spaces=${FALSE}
    ${SPACE}         ${EMPTY}        collapse_spaces=No
    test\tvalue      test\t          collapse_spaces=NO
    YÖTÄ\t           \työtä\ntest    collapse_spaces=${NONE}

Should Start With and collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) ' test?' does not start with 'test'
    ...
    ...    2) 'test value' does not start with 'no test'
    ...
    ...    3) 'YÖTÄ ' does not start with ' yötä test'
    [Template]    Should Start With
    \ttest?          test            collapse_spaces=True
    test\n\ value    test\t\ v       collapse_spaces=${TRUE}
    ${SPACE*5}       ${EMPTY}        collapse_spaces=Yes
    test\n\tvalue    no\ttest        collapse_spaces=TruE
    YÖTÄ\t           \työtä\ttest    collapse_spaces=1

Should Not Start With
    [Documentation]    FAIL 'Hello, world!' starts with 'Hello'
    [Template]    Should Not Start With
    Hello, world!    Hi
    Hello, world!    HELLO
    Hello, world!    Hello

Should Not Start With case-insensitive
    [Documentation]     FAIL  'hello, ss?' starts with 'hello, s'
    [Template]    Should Not Start With
    !Hello!          hELLo           ignore_case=True
    HYVÄÄ YÖTÄ       pahaa           ignore_case=yeah
    Hello, ß?        hello, s        ignore_case=True

Should Not Start With without leading spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'test?' starts with 'test'
    ...
    ...    2) 'test value' starts with 'test'
    ...
    ...    3) repr=yes: 'yötä' starts with 'yötä'
    [Template]    Should Not Start With
    ${SPACE}test?    test        strip_spaces=LEADING
    test value       \t\ntest    strip_spaces=Leading
    \n\työtä         \työtä      repr=yes    strip_spaces=leading

Should Not Start With without trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'test' starts with 'test'
    ...
    ...    2) 'test value' starts with 'test'
    ...
    ...    3) repr=yes: 'yötä' starts with 'yötä'
    [Template]    Should Not Start With
    test${SPACE}    test        strip_spaces=TRAILING
    test value      test\t\n    strip_spaces=Trailing
    yötä\t\n        yötä\n\t    repr=yes    strip_spaces=trailing

Should Not Start With without leading and trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'test' starts with 'test'
    ...
    ...    2) 'test value' starts with 'test'
    ...
    ...    3) repr=yes: 'yötä' starts with 'yötä'
    [Template]    Should Not Start With
    test${SPACE}    test          strip_spaces=True
    test value      test\t\n      strip_spaces=TRUE
    \n\ttest \t     test\t\n      strip_spaces=NO
    \n\työtä\t\n    \t\nyötä\t    repr=yes    strip_spaces=yes

Should Not Start With and do not collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'test\tvalue' starts with 'test'
    ...
    ...    2) '\ttest\n value' starts with '\ttest'
    ...
    ...    3) repr=yes: 'yötä\t\n' starts with 'yötä\t'
    [Template]    Should Not Start With
    test\tvalue       test      collapse_spaces=False
    \ttest\n value    \ttest    collapse_spaces=${FALSE}
    yötä\t\n          yötä\t    repr=yes    collapse_spaces=No

Should Not Start With and collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'test value' starts with 'test'
    ...
    ...    2) ' test value' starts with ' test'
    ...
    ...    3) repr=yes: ' yötä ' starts with ' yötä '
    [Template]    Should Not Start With
    test\tvalue         test        collapse_spaces=True
    \ttest \t\ value    \ttest      collapse_spaces=${TRUE}
    \t\ yötä\t\n        \ yötä\t    repr=yes    collapse_spaces=Sure

Should End With without values
    [Documentation]    FAIL My message
    Should End With    ${LONG}    Nope    My message    values=No values

Should End With
    [Documentation]    FAIL 'Hello, world!' does not end with '?'
    [Template]    Should End With
    Hello, world!    !
    Hello, world!    Hello, world!
    Hello, world!    ?

Should End With case-insensitive
    [Template]      Should End With
    This is it       Is IT            ignore_case=True
    Hello, world!    hello, WORLD!    ignore_case=True
    HYVÄÄ YÖTÄ ß     ä yötä Ss        ignore_case=True

Should End With without leading spaces
    [Documentation]    FAIL 'YÖTÄ' does not end with 'yötä'
    [Template]    Should End With
    ${SPACE}It is    is          strip_spaces=LEADING
    test value       \tvalue     strip_spaces=Leading
    \n\työtä         \nyötä      repr=yes    strip_spaces=leading
    ${SPACE}         ${EMPTY}    strip_spaces=leading
    \n\tYÖTÄ         \työtä      strip_spaces=leading

Should End With without trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'test value' does not end with 'val'
    ...
    ...    2) 'YÖTÄ' does not end with 'yötä'
    [Template]    Should End With
    test\tvalue${SPACE}    value             strip_spaces=TRAILING
    test value             val\t             strip_spaces=Trailing
    yötä\t \n              yötä\n            repr=yes    strip_spaces=trailing
    ${SPACE}               ${EMPTY}          strip_spaces=trailing
    YÖTÄ\n \t              yötä\t${SPACE}    strip_spaces=trailing

Should End With without leading and trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'some test' does not end with 'test\t'
    ...
    ...    2) 'YÖTÄ' does not end with 'yötä'
    [Template]    Should End With
    \ttest?${SPACE}    ${SPACE}?\t    strip_spaces=True
    test\ \ value      \te            strip_spaces=truE
    ${SPACE}yötä\t     \ yötä\t       repr=yes    strip_spaces=yes
    ${SPACE}           ${EMPTY}       strip_spaces=true
    some test          test\t         strip_spaces=False
    ${SPACE}YÖTÄ\t     \työtä\t       strip_spaces=true

Should End With and do not collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) '\ttest\ \ ?' does not end with '\n?'
    ...
    ...    2) repr=yes: '\t\nyötä\t' does not end with '\ Yötä'
    [Template]    Should End With
    \ttest\ \ ?       \n?         collapse_spaces=False
    \t\nyötä\t        \ Yötä      repr=yes    collapse_spaces=${FALSE}
    some\ \ test\t    \ test\t    collapse_spaces=No

Should End With and collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) ' test ?' does not end with 'T ?'
    ...
    ...    2) repr=yes: ' yötä ' does not end with ' Yötä'
    [Template]    Should End With
    \ttest\ \ ?       T\n?          collapse_spaces=True
    \t\nyötä\t        \ Yötä        repr=yes    collapse_spaces=${TRUE}
    some\ \ test\n    \t\ttest\t    collapse_spaces=Yes

Should Not End With
    [Documentation]    FAIL Message only
    [Template]    Should Not End With
    Hello!    Hello
    Hillo!    !    Message only    No Values

Should Not End With case-insensitive
    [Documentation]     FAIL  'hello, ss!' ends with 'hello, ss!'
    [Template]    Should Not End With
    Hello!           hELLo            ignore_case=True
    HYVÄÄ YÖTÄ       hyvää            ignore_case=yeah
    Hello, ß!        HELLO, SS!       ignore_case=True

Should Not End With without leading spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'It is' ends with 'is'
    ...
    ...    2) 'test value' ends with 'value'
    ...
    ...    3) repr=yes: 'yötä' ends with 'yötä'
    [Template]    Should Not End With
    ${SPACE}It is    is         strip_spaces=LEADING
    test value       \nvalue    strip_spaces=Leading
    \n \työtä        \työtä     repr=yes    strip_spaces=leading

Should Not End With without trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'It is' ends with 'is'
    ...
    ...    2) 'test value' ends with 'value'
    ...
    ...    3) repr=yes: 'yötä' ends with 'yötä'
    [Template]    Should Not End With
    It is\t \n      is          strip_spaces=TRAILING
    test value      value\t     strip_spaces=Trailing
    yötä${SPACE}    yötä\t\n    repr=yes    strip_spaces=trailing

Should Not End With without leading and trailing spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) 'test?' ends with '?'
    ...
    ...    2) 'test\ \ value' ends with 'e'
    ...
    ...    3) repr=yes: 'yötä' ends with 'yötä'
    [Template]    Should Not End With
    \ttest?${SPACE}    ${SPACE}?\t    strip_spaces=True
    test\ \ value\n    \te            strip_spaces=truE
    \n \työtä\t\n      \ yötä\t\n     repr=yes    strip_spaces=yes
    some test          test\t         strip_spaces=NO

Should Not End With and do not collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) '\ttest\t\n?' ends with '\t\n?'
    ...
    ...    2) 'test\ \nvalue' ends with 'e'
    ...
    ...    3) repr=yes: '\työtä\t' ends with 'yötä\t'
    [Template]    Should Not End With
    \ttest\t\n?      \t\n?       collapse_spaces=False
    test\ \nvalue    e           collapse_spaces=${FALSE}
    \työtä\t         yötä\t      repr=yes    collapse_spaces=FalsE
    some\ test       \ \ test    collapse_spaces=NO

Should Not End With and collapse spaces
    [Documentation]    FAIL Several failures occurred:
    ...
    ...    1) ' test ?' ends with ' ?'
    ...
    ...    2) 'test value' ends with 'e'
    ...
    ...    3) repr=yes: ' yötä ' ends with 'yötä '
    ...
    ...    4) 'some test' ends with ' test'
    [Template]    Should Not End With
    \ttest\ \ ?      \t\n?       collapse_spaces=True
    test\t\nvalue    e           collapse_spaces=${TRUE}
    \työtä\t         yötä\t      repr=yes    collapse_spaces=Yes
    some\ test       \ \ test    collapse_spaces=1
