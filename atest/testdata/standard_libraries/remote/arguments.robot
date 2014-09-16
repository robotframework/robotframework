*** Settings ***
Library           Remote    http://127.0.0.1:${PORT}
Suite Setup       Set Log Level    DEBUG

*** Variables ***
${PORT}           8270

*** Test Cases ***
No Arguments
    [Template]    Arguments Should Be Accepted
    ${EMPTY}    No Arguments

Required Arguments
    [Template]    Arguments Should Be Accepted
    some argument    One Argument    some argument
    first argument, second argument    Two Arguments    first argument    second argument
    1, 2, 3 (int), 4, 5    Five Arguments    1    2    ${3}    4    5

Arguments With Default Values
    [Template]    Arguments Should Be Accepted
    one, two, three    Arguments With Default Values    one    two    three
    one, two, 3    Arguments With Default Values    one    two
    one, 2 (int), 3    Arguments With Default Values    one

Named Arguments
    ${result} =    Arguments With Default Values    first    arg2=second
    Should Be Equal    ${result}    first, second, 3
    ${result} =    Arguments With Default Values    arg1=first    arg2=second
    Should Be Equal    ${result}    first, second, 3
    ${result} =    Arguments With Default Values    arg2=second    arg1=first
    Should Be Equal    ${result}    first, second, 3
    ${result} =    Arguments With Default Values    first    arg3=third
    Should Be Equal    ${result}    first, 2, third
    ${result} =    Arguments With Default Values    arg3=C    arg1=A    arg2=B
    Should Be Equal    ${result}    A, B, C

Variable Number Of Arguments
    [Template]    Arguments Should Be Accepted
    ${EMPTY}    Varargs
    One argument    Varargs    One argument
    Three, arguments, now    Varargs    Three    arguments    now
    1, 2, 3, 4 (int), 5    Varargs    1    2    3    ${4}    5

Required Arguments, Default Values and Varargs
    [Template]    Arguments Should Be Accepted
    Hello, world    Required Defaults And Varargs    Hello
    Hi, tellus    Required Defaults And Varargs    Hi    tellus
    Hello, again, world    Required Defaults And Varargs    Hello    again    world
    1, 2, 3, 4, 5 (int)    Required Defaults And Varargs    1    2    3    4    ${5}

No kwargs
    ${result} =    Kwargs
    Should Be Equal    ${result}    ${EMPTY}

One kwarg
    ${result} =    Kwargs    foo=bar
    Should Be Equal    ${result}    foo:bar

Multiple kwargs
    ${result} =    Kwargs    a=1    c=3    d=4    b=2
    Should Be Equal    ${result}    a:1, b:2, c:3, d:4

Args and kwargs
    ${result} =    Args and kwargs    arg
    Should Be Equal    ${result}    arg, default2
    ${result} =    Args and kwargs    arg    foo=bar
    Should Be Equal    ${result}    arg, default2, foo:bar
    ${result} =    Args and kwargs    a    arg2=b    c=3    d=4
    Should Be Equal    ${result}    a, b, c:3, d:4
    ${result} =    Args and kwargs    arg2=b    c=3    d=4
    Should Be Equal    ${result}    default1, b, c:3, d:4

Varargs and kwargs
    ${result} =    Varargs and kwargs
    Should Be Equal    ${result}    ${EMPTY}
    ${result} =    Varargs and kwargs    foo=bar
    Should Be Equal    ${result}    foo:bar
    ${result} =    Varargs and kwargs    arg    foo=bar
    Should Be Equal    ${result}    arg, foo:bar
    ${result} =    Varargs and kwargs    a    b    c    d=4    e=5    f=6
    Should Be Equal    ${result}    a, b, c, d:4, e:5, f:6

Args, varargs and kwargs
    ${result} =    Args varargs and kwargs    arg
    Should Be Equal    ${result}    arg, default2
    ${result} =    Args varargs and kwargs    arg    foo=bar
    Should Be Equal    ${result}    arg, default2, foo:bar
    ${result} =    Args varargs and kwargs    arg2=foo    foo=bar
    Should Be Equal    ${result}    default1, foo, foo:bar
    ${result} =    Args varargs and kwargs    a    arg2=b    c=3
    Should Be Equal    ${result}    a, b, c:3
    ${result} =    Args varargs and kwargs    c=3    arg1=a    d=4    arg2=b
    Should Be Equal    ${result}    a, b, c:3, d:4
    ${result} =    Args varargs and kwargs    a    b    c    d    e=5    f=6
    Should Be Equal    ${result}    a, b, c, d, e:5, f:6

Using Arguments When No Accepted
    [Documentation]    FAIL Keyword 'Remote.No Arguments' expected 0 arguments, got 1.
    No Arguments    not allowed

Using Positional Arguments When Only Kwargs Accepted
    [Documentation]    FAIL Keyword 'Remote.Kwargs' expected 0 non-keyword arguments, got 1.
    Kwargs    not allowed

Too Few Arguments When Using Only Required Args
    [Documentation]    FAIL Keyword 'Remote.One Argument' expected 1 argument, got 0.
    One Argument

Too Many Arguments When Using Only Required Args
    [Documentation]    FAIL Keyword 'Remote.Two Arguments' expected 2 arguments, got 3.
    Two Arguments    too    many    arguments

Too Few Arguments When Using Default Values
    [Documentation]    FAIL Keyword 'Remote.Arguments With Default Values' expected 1 to 3 arguments, got 0.
    Arguments With Default Values

Too Many Arguments When Using Default Values
    [Documentation]    FAIL Keyword 'Remote.Arguments With Default Values' expected 1 to 3 arguments, got 5.
    Arguments With Default Values    this    is    way    too    much

Too Few Arguments When Using Varargs
    [Documentation]    FAIL Keyword 'Remote.Required Defaults And Varargs' expected at least 1 argument, got 0.
    Required Defaults And Varargs

Named arguments before positional
    [Documentation]    FAIL Keyword 'Remote.Args And Kwargs' got positional argument after named arguments.
    Args and kwargs    this=wont    work

*** Keywords ***
Arguments Should Be Accepted
    [Arguments]    ${expected}    ${keyword}    @{arguments}
    ${result} =    Run Keyword    ${keyword}    @{arguments}
    Should Be Equal    ${result}    ${expected}
