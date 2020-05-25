*** Settings ***
Library            DynamicWithoutKwargs.py

*** Variables ***
${a}               a
${b}               b

*** Test Cases ***
Simple usage
    ${ret} =    One Arg    arg=value
    Should Be Equal    ${ret}    value
    ${ret} =    Two Args    first=1    second=2
    Should Be Equal    ${ret}    1, 2
    ${ret} =    Four Args    a=A    b=B    c=C    d=D
    Should Be Equal    ${ret}    A, B, C, D

Variable in name
    ${ret} =    One Arg    ${a}rg=value
    Should Be Equal    ${ret}    value
    ${ret} =    Four Args    ${a}=A    ${b}=B    c=C    d=D
    Should Be Equal    ${ret}    A, B, C, D

Order does not matter
    ${ret} =    Two Args    second=bar    first=foo
    Should Be Equal    ${ret}    foo, bar
    ${ret} =    Four Args    b=B    d=D    c=C    ${a}=A
    Should Be Equal    ${ret}    A, B, C, D

Last named wins
    ${ret} =    Two Args    first=foo    second=bar    second=!!!    first=WIN
    Should Be Equal    ${ret}    WIN, !!!
    ${ret} =    Four Args    b=B    d=D    c=C    a=A    a=X    ${b}=Y    c=Z
    ...    ${a}=W    d=?    c=N    b=I    d=!
    Should Be Equal    ${ret}    W, I, N, !

Positional and named
    ${ret} =    Two Args    foo    second=bar
    Should Be Equal    ${ret}    foo, bar
    ${ret} =    Four Args    A    B    d=D    c=C
    Should Be Equal    ${ret}    A, B, C, D

Values with defaults can be omitted at the end
    ${ret} =    Four Args    A    B    C
    Should Be Equal    ${ret}    A, B, C
    ${ret} =    Four Args    a=A    b=B    c=C
    Should Be Equal    ${ret}    A, B, C
    ${ret} =    Four Args    a=A
    Should Be Equal    ${ret}    A

Values with defaults can be omitted in the middle
    [Documentation]    Default values are used to fill the gaps.
    ${ret} =    Four Args    a=A    d=D
    Should Be Equal    ${ret}    A, 2, 3 (int), D
    ${ret} =    Four Args    d=D
    Should Be Equal    ${ret}    1, 2, 3 (int), D
    ${ret} =    Four Args    c=C
    Should Be Equal    ${ret}    1, 2, C

Non-string values
    ${ret} =    One Arg    arg=${42}
    Should Be Equal    ${ret}    42 (int)
    ${ret} =    Two Args    first=${1}    second=${2}
    Should Be Equal    ${ret}    1 (int), 2 (int)
    ${ret} =    Four Args    a=${1}    d=${True}
    Should Be Equal    ${ret}    1 (int), 2, 3 (int), True (bool)

Nön-ÄSCII values
    ${ret} =    Two Args    first=ensimmäinen    second=官话
    Should Be Equal    ${ret}    ensimmäinen, 官话

Nön-ÄSCII names
    ${ret} =    Nön-ÄSCII names    官话=спасибо     nönäscii=官话
    Should Be Equal    ${ret}    官话, спасибо

Equal sign in value
    ${ret} =    One Arg    arg=bar=quux
    Should Be Equal    ${ret}    bar=quux

Equal sign from variable
    ${value} =    Set Variable    arg=value
    ${ret} =   One Arg     ${value}
    Should Be Equal    ${ret}    arg=value

Equal sign with non-existing name
    ${ret} =    One Arg    not=arg
    Should Be Equal    ${ret}    not=arg

Escaping equal sign
    ${ret} =    One Arg    arg\=escaped
    Should Be Equal    ${ret}     arg=escaped

Escaping value
    ${ret} =    Four Args    a=\${notvar}    b=\n    c=\\n    d=\
    Should Be Equal    ${ret}     \${notvar}, \n, \\n,${SPACE}
    ${ret} =    Defaults w/ Specials    d=\
    Should Be Equal    ${ret}     \${notvar}, \n, \\n,${SPACE}

Inside "Run Keyword"
    ${ret} =    Run Keyword    Four Args    A    B    d=D    c=C
    Should Be Equal    ${ret}    A, B, C, D

Varargs without naming works
    ${ret} =    Args & Varargs    foo    bar    dar
    Should be equal    ${ret}    foo, bar, dar
    ${ret} =    Args & Varargs    foo    bar=bar    dar
    Should be equal    ${ret}    foo, bar=bar, dar
    ${ret} =    Args & Varargs    foo    b\=bar    dar
    Should be equal    ${ret}    foo, b=bar, dar
    ${ret} =    Args & Varargs    foo    bar    quux=qaax
    Should be equal    ${ret}    foo, bar, quux=qaax

Naming without varargs works
    ${ret} =    Args & Varargs    foo    b=bar
    Should be equal    ${ret}     foo, bar
    ${ret} =    Args & Varargs    a=1    b=2
    Should be equal    ${ret}     1, 2
    ${ret} =    Args & Varargs    b=B    a=A
    Should be equal    ${ret}     A, B

Positional after named 1
    [Documentation]    FAIL Keyword 'DynamicWithoutKwargs.Args & Varargs' got positional argument after named arguments.
    Args & Varargs    foo    b=bar    dar

Positional after named 2
    [Documentation]    FAIL Keyword 'DynamicWithoutKwargs.Args & Varargs' got positional argument after named arguments.
    Args & Varargs    foo    b=bar    @{EMPTY}

Positional after named 3
    [Documentation]    FAIL Keyword 'DynamicWithoutKwargs.Two Args' got positional argument after named arguments.
    Two Args    first=1    oops

Missing argument
    [Documentation]    FAIL Keyword 'DynamicWithoutKwargs.Args & Varargs' missing value for argument 'a'.
    Args & Varargs    b=value

Both positional and named value 1
    [Documentation]    FAIL Keyword 'DynamicWithoutKwargs.Two Args' got multiple values for argument 'first'.
    Two Args    1    first=oops

Both positional and named value 2
    [Documentation]    FAIL Keyword 'DynamicWithoutKwargs.Args & Varargs' got multiple values for argument 'a'.
    Args & Varargs    A    B   a=ooops
