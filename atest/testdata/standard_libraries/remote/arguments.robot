*** Settings ***
Library           Remote    http://127.0.0.1:${PORT}
Suite Setup       Set Log Level    DEBUG
Test Template     Arguments Should Be Accepted

*** Variables ***
${PORT}           8270

*** Test Cases ***
No Arguments
    ${EMPTY}                 No Arguments

Required Arguments
    some argument            One Argument                     some argument
    first arg, second arg    Two Arguments                    first arg    second arg
    1, 2, 3 (int), 4, 5      Five Arguments                   1    2    ${3}    4    5

Arguments With Default Values
    one, two, three          Arguments With Default Values    one    two    three
    one, two, 3              Arguments With Default Values    one    two
    one, 2 (int), 3          Arguments With Default Values    one

Defaults as tuples
    eka, 2 (int)             Defaults as tuples
    xxx, 2 (int)             Defaults as tuples               xxx
    xxx, 3 (int)             Defaults as tuples               xxx     3

Arguent conversion based on defaults
    xxx, 3 (int)             Defaults as tuples               xxx     3
    xxx, 3.14 (float)        Defaults as tuples               xxx     3.14
    xxx, yyy                 Defaults as tuples               xxx     yyy
    0 (int), 3 (int)         Defaults as tuples               ${0}    3

Named Arguments
    first, second, 3         Arguments With Default Values    first    arg2=second
    first, second, 3         Arguments With Default Values    arg1=first    arg2=second
    first, second, 3         Arguments With Default Values    arg2=second    arg1=first
    first, 2 (int), third    Arguments With Default Values    first    arg3=third
    A, B, C                  Arguments With Default Values    arg3=C    arg1=A    arg2=B

Variable Number Of Arguments
    ${EMPTY}                 Varargs
    One argument             Varargs                          One argument
    Three, arguments, now    Varargs                          Three    arguments    now
    1, 2, 3, 4 (int), 5      Varargs                          1    2    3    ${4}    5

Required Arguments, Default Values and Varargs
    Hello, world             Required Defaults And Varargs    Hello
    Hi, tellus               Required Defaults And Varargs    Hi    tellus
    Hello, again, world      Required Defaults And Varargs    Hello    again    world
    1, 2, 3, 4, 5 (int)      Required Defaults And Varargs    1    2    3    4    ${5}

No kwargs
    ${EMPTY}                 Kwargs

One kwarg
    foo:bar                  Kwargs                           foo=bar

Multiple kwargs
    a:1, b:2, c:3, d:4       Kwargs                           a=1    c=3    d=4    b=2

Keyword-only args
    kwo:value                Kw Only Arg                      kwo=value

Keyword-only args with default
    k1:default, k2:value     Kw Only Arg With Default         k2=value
    k1:xxx, k2:yyy           Kw Only Arg With Default         k2=yyy    k1=xxx

Args and kwargs
    arg, default2            Args and kwargs                  arg
    arg, default2, kw:foo    Args and kwargs                  arg    kw=foo
    a, b, c:3, d:4           Args and kwargs                  a    arg2=b    c=3    d=4
    default1, b, c:3, d:4    Args and kwargs                  arg2=b    c=3    d=4

Varargs and kwargs
    ${EMPTY}                 Varargs and kwargs
    foo:bar                  Varargs and kwargs               foo=bar
    arg, foo:bar             Varargs and kwargs               arg    foo=bar
   a, b, c, d:4, e:5, f:6    Varargs and kwargs               a    b    c    d=4    e=5    f=6

All arg types
    arg, default, kwo1:default, kwo2:2
    ...                      All arg types                    arg    kwo2=2
    arg, default, kw:foo, kwo1:default, kwo2:bar
    ...                      All arg types                    arg    kw=foo    kwo2=bar
    1, 2, kw:3, kwo1:4, kwo2:5
    ...                      All arg types                    arg2=2    kwo2=5    kwo1=4    kw=3    arg1=1
    a, b, c:3, kwo1:default, kwo2:x
    ...                      All arg types                    a    arg2=b    c=3    kwo2=x
    a, b, c:3, d:4, kwo1:default, kwo2:
    ...                      All arg types                    c=3    arg1=a    kwo2=    d=4    arg2=b
    a, b, c, d, e:5, f:6, kwo1:7, kwo2:8
    ...                      All arg types                    a    b    c    d    e=5    f=6    kwo2=8    kwo1=7

Using Arguments When No Accepted
    [Documentation]    FAIL Keyword 'Remote.No Arguments' expected 0 arguments, got 1.
    [Template]    NONE
    No Arguments    not allowed

Using Positional Arguments When Only Kwargs Accepted
    [Documentation]    FAIL Keyword 'Remote.Kwargs' expected 0 non-named arguments, got 1.
    [Template]    NONE
    Kwargs    not allowed

Too Few Arguments When Using Only Required Args
    [Documentation]    FAIL Keyword 'Remote.One Argument' expected 1 argument, got 0.
    [Template]    NONE
    One Argument

Too Many Arguments When Using Only Required Args
    [Documentation]    FAIL Keyword 'Remote.Two Arguments' expected 2 arguments, got 3.
    [Template]    NONE
    Two Arguments    too    many    arguments

Too Few Arguments When Using Default Values
    [Documentation]    FAIL Keyword 'Remote.Arguments With Default Values' expected 1 to 3 arguments, got 0.
    [Template]    NONE
    Arguments With Default Values

Too Many Arguments When Using Default Values
    [Documentation]    FAIL Keyword 'Remote.Arguments With Default Values' expected 1 to 3 arguments, got 5.
    [Template]    NONE
    Arguments With Default Values    this    is    way    too    much

Too Few Arguments When Using Varargs
    [Documentation]    FAIL Keyword 'Remote.Required Defaults And Varargs' expected at least 1 argument, got 0.
    [Template]    NONE
    Required Defaults And Varargs

Named arguments before positional
    [Documentation]    FAIL Keyword 'Remote.Args And Kwargs' got positional argument after named arguments.
    [Template]    NONE
    Args and kwargs    this=wont    work

Argument types as list
    [Template]    NONE
    Argument types as list    42    42    {'a': 1, 'b': u'ä'}    {}

Argument types as dict
    [Template]    NONE
    Argument types as dict    42    42    {'a': 1, 'b': u'ä'}    {}

*** Keywords ***
Arguments Should Be Accepted
    [Arguments]    ${expected}    ${keyword}    @{args}    &{kwargs}
    ${result} =    Run Keyword    ${keyword}    @{args}    &{kwargs}
    Should Be Equal    ${result}    ${expected}
