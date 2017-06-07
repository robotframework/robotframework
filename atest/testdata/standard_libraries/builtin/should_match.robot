*** Settings ***
Variables         variables_to_verify.py

*** Test Cases ***
Should Match
    [Documentation]    FAIL    Failure: 'NOK' does not match 'H*K'
    [Template]    Should Match
    abcdefghijklmnopqrstuvwxyz    *
    abcdefghijklmnopqrstuvwxyz    ?*?efg*p*t?vw*z
    NOK                           ???
    NOK                           H*K    Failure

Should Match case-insensitive
    [Template]    Should Match
    Hello!    heLLo!    ignore_case=True
    Hillo?    h?ll*     ignore_case=yes

Should Match with bytes containing non-ascii characters
    [Documentation]    FAIL    '${BYTES WITH NON ASCII}' does not match 'hyva'
    [Template]    Should Match
    ${BYTES WITH NON ASCII}    ${BYTES WITH NON ASCII}
    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}

Should Not Match
    [Documentation]    FAIL    'Hello world' matches '?ello*'
    [Template]    Should Not Match
    this string does not    match this pattern
    Case matters            case matters
    Hello world             ?ello*

Should Not Match case-insensitive
    [Documentation]    FAIL    Fails: 'hillo?' matches 'h?ll*'
    [Template]    Should Not Match
    Hello!    heLLo    ignore_case=True
    Hillo?    h?ll*    ignore_case=yes    msg=Fails

Should Not Match with bytes containing non-ascii characters
    [Documentation]    FAIL    '${BYTES WITH NON ASCII}' matches '${BYTES WITH NON ASCII}'
    [Template]    Should Not Match
    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}
    ${BYTES WITH NON ASCII}    ${BYTES WITH NON ASCII}

Should Match Regexp
    [Documentation]    FAIL    Something failed
    [Template]    Should Match Regexp
    Foo: 42        \\w+: \\d{2}
    IGNORE CASE    (?i)case
    ${EMPTY}       whatever    Something failed    No values

Should Match Regexp returns match and groups
    ${ret} =    Should Match Regexp    This is a multiline\nstring!!    (?im)^STR\\w+!!
    ${match}    ${group} =    Should Match Regexp    ${ret}    ^(\\w+)!!$
    Should Be Equal    ${match}    ${ret}
    Should Be Equal    ${group}    string
    ${match}    @{groups} =    Should Match Regexp    Foo: 42 (xxx)    ^(Fo+)([:.;]) (\\d+?)
    Should Be Equal    ${match}    Foo: 4
    Should Be True    @{groups} == ['Foo', ':', '4']
    ${match}    ${group1}    ${group2} =    Should Match Regexp    Hello, (my) World!!!!!    (?ix)^hel+o,\\s # Comment \n \\((my|your)\\)\\ WORLD(!*)$
    Should Be Equal    ${match}    Hello, (my) World!!!!!
    Should Be Equal    ${group1}    my
    Should Be Equal    ${group2}    !!!!!

Should Match Regexp with bytes containing non-ascii characters
    [Documentation]    FAIL    '${BYTES WITH NON ASCII}' does not match 'hyva'
    [Template]    Should Match Regexp
    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}

Should Not Match Regexp
    [Documentation]    FAIL    'James Bond 007' matches '^J\\w{4}\\sB[donkey]+ \\d*$'
    [Template]    Should Not Match Regexp
    this string does not    match this pattern
    James Bond 007          ^J\\w{4}\\sB[donkey]+ \\d*$
