*** Settings ***
Library           DynamicPositionalOnly.py

*** Test Cases ***
One Argument
    ${result} =    One Argument    value
    Should be equal    ${result}    one argument-('value',)
    ${result} =    One Argument    one=value
    Should be equal    ${result}    one argument-('one=value',)
    ${result} =    One Argument    foo=value
    Should be equal    ${result}    one argument-('foo=value',)

Three arguments
    ${result} =    Three Arguments    a    b    c
    Should be equal    ${result}    three arguments-('a', 'b', 'c')
    ${result} =    Three Arguments    x=a    y=b    z=c
    Should be equal    ${result}    three arguments-('x=a', 'y=b', 'z=c')
    ${result} =    Three Arguments    a=a    b=b    c=c
    Should be equal    ${result}    three arguments-('a=a', 'b=b', 'c=c')

Pos and named
    ${result} =    with normal    a    b
    Should be equal    ${result}    with normal-('a', 'b')
    ${result} =    with normal    posonly=posonly    normal=111
    Should be equal    ${result}    with normal-('posonly=posonly',)-{'normal': '111'}
    ${result} =    with normal    aaa    normal=111
    Should be equal    ${result}    with normal-('aaa',)-{'normal': '111'}

Pos and names too few arguments
    [Documentation]    FAIL Keyword 'DynamicPositionalOnly.With Normal' expected 2 arguments, got 1.
    with normal    normal=aaa

Three arguments too many arguments
    [Documentation]    FAIL Keyword 'DynamicPositionalOnly.Three Arguments' expected 3 arguments, got 4.
    Three Arguments    a    b    c    /

Pos with default
    ${result} =    default str    a
    Should be equal    ${result}    default str-('a',)
    ${result} =    default str    a    optional=b
    Should be equal    ${result}    default str-('a', 'optional=b')
    ${result} =    default str    optional=b
    Should be equal    ${result}    default str-('optional=b',)
    ${result} =    default tuple    a
    Should be equal    ${result}    default tuple-('a',)
    ${result} =    default tuple    a    optional=b
    Should be equal    ${result}    default tuple-('a', 'optional=b')
    ${result} =    default tuple    optional=b
    Should be equal    ${result}    default tuple-('optional=b',)
    ${result} =    default tuple    optional=b    optional=c
    Should be equal    ${result}    default tuple-('optional=b', 'optional=c')
    Arg with separator    /one=
    Should be equal    ${result}    default tuple-('optional=b', 'optional=c')

All args
    ${result} =    all args kw    other    value    1    2    kw1=1    kw2=2
    Should be equal    ${result}    all args kw-('other', 'value', '1', '2')-{'kw1': '1', 'kw2': '2'}
    ${result} =    all args kw    other
    Should be equal    ${result}    all args kw-('other',)
    ${result} =    all args kw
    Should be equal    ${result}    all args kw-()
