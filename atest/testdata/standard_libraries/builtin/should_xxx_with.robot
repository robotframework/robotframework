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

Should Start With without values
    [Documentation]    FAIL My message
    Should Start With    ${LONG}    Nope    My message    values=No values

Should Start With without leading spaces
    [Documentation]    FAIL    'YÖTÄ' does not start with 'yötä'
    [Template]    Should Start With
    San Diego!         San Diego   strip_spaces=leading
    ${SPACE}\ttest?    test        strip_spaces=LEADING
    test value         \ttest      strip_spaces=Leading
    \nyötä             \työtä      repr=yes    strip_spaces=leading
    ${SPACE}           ${EMPTY}    strip_spaces=leading
    ${SPACE}YÖTÄ       \nyötä      strip_spaces=leading

Should Start With without trailing spaces
    [Documentation]    FAIL  'YÖTÄ' does not start with 'yötä'
    [Template]    Should Start With
    San Diego!             San Diego         strip_spaces=trailing
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
    San Diego!         San Diego         strip_spaces=TRUE
    \ttest?${SPACE}    ${SPACE}test\t    strip_spaces=True
    test\ \ value      \ttest\ \ v       strip_spaces=truE
    \nyötä\n\t         yötä\t            repr=yes    strip_spaces=yes
    ${SPACE}           ${EMPTY}          strip_spaces=true
    test value         test\t            strip_spaces=NO
    \t\n\ YÖTÄ\t       \työtä\t\n        strip_spaces=true

Should Not Start With
    [Documentation]    FAIL 'Hello, world!' starts with 'Hello'
    [Template]    Should Not Start With
    Hello, world!    Hi
    Hello, world!    HELLO
    Hello, world!    Hello

Should Not Start With case-insensitive
    [Documentation]     FAIL  'hello, world?' starts with 'hello, world'
    [Template]    Should Not Start With
    !Hello!          hELLo           ignore_case=True
    HYVÄÄ YÖTÄ       pahaa           ignore_case=yeah
    Hello, world?    hello, WORLD    ignore_case=True

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
    ...    1)  'test' starts with 'test'
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
    HYVÄÄ YÖTÄ       ä yötä           ignore_case=True

Should End With without leading spaces
    [Documentation]    FAIL 'YÖTÄ' does not end with 'yötä'
    [Template]    Should End With
    San Diego        Diego       strip_spaces=leading
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
    San Diego              Diego             strip_spaces=trailing
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
    San Diego          Diego          strip_spaces=TRUE
    \ttest?${SPACE}    ${SPACE}?\t    strip_spaces=True
    test\ \ value      \te            strip_spaces=truE
    ${SPACE}yötä\t     \ yötä\t       repr=yes    strip_spaces=yes
    ${SPACE}           ${EMPTY}       strip_spaces=true
    some test          test\t         strip_spaces=False
    ${SPACE}YÖTÄ\t     \työtä\t       strip_spaces=true

Should Not End With
    [Documentation]    FAIL Message only
    [Template]    Should Not End With
    Hello!    Hello
    Hillo!    !    Message only    No Values

Should Not End With case-insensitive
    [Documentation]     FAIL  'hello, world!' ends with 'hello, world!'
    [Template]    Should Not End With
    Hello!           hELLo            ignore_case=True
    HYVÄÄ YÖTÄ       hyvää            ignore_case=yeah
    Hello, world!    hello, WORLD!    ignore_case=True

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
