*** Settings ***
Library            DynamicWithKwargs.py

*** Variables ***
${a}               a
${b}               b

*** Test Cases ***
Simple usage
    ${ret} =    One Arg    arg=value
    Should Be Equal    ${ret}    arg:value
    ${ret} =    Two Args    first=1    second=2
    Should Be Equal    ${ret}    first:1, second:2
    ${ret} =    Four Args    a=A    b=B    c=C    d=D
    Should Be Equal    ${ret}    a:A, b:B, c:C, d:D
    ${ret} =    Kwargs    a=A    b=B    c=C    d=D
    Should Be Equal    ${ret}    a:A, b:B, c:C, d:D

Variable in name
    ${ret} =    One Arg    ${a}rg=value
    Should Be Equal    ${ret}    arg:value
    ${ret} =    Four Args    ${a}=A    ${b}=B    c=C    d=D
    Should Be Equal    ${ret}    a:A, b:B, c:C, d:D
    ${ret} =    Kwargs    ${a}=A    ${b}=B    c=C    d=D    ${a.upper()}=first
    Should Be Equal    ${ret}    A:first, a:A, b:B, c:C, d:D

Order does not matter
    ${ret} =    Two Args    second=bar    first=foo
    Should Be Equal    ${ret}    first:foo, second:bar
    ${ret} =    Four Args    b=B    d=D    c=C    ${a}=A
    Should Be Equal    ${ret}    a:A, b:B, c:C, d:D

Last named wins
    ${ret} =    Two Args    first=foo    second=bar    second=!!!    first=WIN
    Should Be Equal    ${ret}    first:WIN, second:!!!
    ${ret} =    Four Args    b=B    d=D    c=C    a=A    a=X    ${b}=Y    c=Z
    ...    ${a}=W    d=?    c=N    b=I    d=!
    Should Be Equal    ${ret}    a:W, b:I, c:N, d:!
    ${ret} =    Kwargs    b=B    d=D    c=C    a=A    a=X    b=Y    c=Z
    ...    a=W    d=?    c=N    ${b}=I    d=!
    Should Be Equal    ${ret}    a:W, b:I, c:N, d:!

Positional and named
    ${ret} =    Two Args    foo    second=bar
    Should Be Equal    ${ret}    foo, second:bar
    ${ret} =    Four Args    A    B    d=D    c=C
    Should Be Equal    ${ret}    A, B, c:C, d:D
    ${ret} =    Args & Kwargs    A    B    C    k=1    w=2
    Should Be Equal    ${ret}    A, B, C, k:1, w:2
    ${ret} =    Args, Varargs & Kwargs    A    B    C    D    E    k=1    w=2
    Should Be Equal    ${ret}    A, B, C, D, E, k:1, w:2

Values with defaults can be omitted at the end
    ${ret} =    Four Args    a=A    b=B    c=C
    Should Be Equal    ${ret}    a:A, b:B, c:C
    ${ret} =    Four Args    a=A
    Should Be Equal    ${ret}    a:A
    ${ret} =    Args & Kwargs    a=A    k=1    w=2
    Should Be Equal    ${ret}    a:A, k:1, w:2

Values with defaults can be omitted in the middle
    ${ret} =    Four Args    a=A    d=D
    Should Be Equal    ${ret}    a:A, d:D
    ${ret} =    Four Args    d=D
    Should Be Equal    ${ret}    d:D
    ${ret} =    Four Args    c=C
    Should Be Equal    ${ret}    c:C
    ${ret} =    Args & Kwargs    k=1    w=2    c=C    a=A
    Should Be Equal    ${ret}    a:A, c:C, k:1, w:2

Non-string values
    ${ret} =    One Arg    arg=${42}
    Should Be Equal    ${ret}    arg:42 (int)
    ${ret} =    Two Args    first=${1}    second=${2}
    Should Be Equal    ${ret}    first:1 (int), second:2 (int)
    ${ret} =    Four Args    a=${1}    d=${True}
    Should Be Equal    ${ret}    a:1 (int), d:True (bool)
    ${ret} =    Kwargs    a=${1}    b=${2.0}    c=${False}
    Should Be Equal    ${ret}    a:1 (int), b:2.0 (float), c:False (bool)

Nön-ÄSCII values
    ${ret} =    Two Args    first=ensimmäinen    second=官话
    Should Be Equal    ${ret}    first:ensimmäinen, second:官话
    ${ret} =    Kwargs    a=Ä    o=Ö    third=官话
    Should Be Equal    ${ret}    a:Ä, o:Ö, third:官话

Nön-ÄSCII names
    ${ret} =    Nön-ÄSCII names    官话=спасибо     nönäscii=官话
    Should Be Equal    ${ret}    nönäscii:官话, 官话:спасибо
    ${ret} =    Kwargs    å=Å    官话=спасибо
    Should Be Equal    ${ret}    å:Å, 官话:спасибо

Equal sign in value
    ${ret} =    One Arg    arg=bar=quux
    Should Be Equal    ${ret}    arg:bar=quux
    ${ret} =    Kwargs    a=b=c    x==
    Should Be Equal    ${ret}    a:b=c, x:=

Equal sign in name
    ${ret} =    Kwargs    a\=b=c    x\==
    Should Be Equal    ${ret}    a=b:c, x=:

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
    Should Be Equal    ${ret}     a:\${notvar}, b:\n, c:\\n, d:
    ${ret} =    Defaults w/ Specials    d=\
    Should Be Equal    ${ret}     d:

Inside "Run Keyword"
    ${ret} =    Run Keyword    Four Args    A    B    d=D    c=C
    Should Be Equal    ${ret}    A, B, c:C, d:D
    ${ret} =    Run Keyword    Args & Kwargs    A    B    d=D    c=C    e=E
    Should Be Equal    ${ret}    A, B, c:C, d:D, e:E

Varargs without naming works
    ${ret} =    Args & Varargs    foo    bar    dar
    Should be equal    ${ret}    foo, bar, dar
    ${ret} =    Args & Varargs    foo    bar=bar    dar
    Should be equal    ${ret}    foo, bar=bar, dar
    ${ret} =    Args & Varargs    foo    b\=bar    dar
    Should be equal    ${ret}    foo, b=bar, dar
    ${ret} =    Args & Varargs    foo    bar    quux=qaax
    Should be equal    ${ret}    foo, bar, quux=qaax
    ${ret} =    Args, Varargs & Kwargs    foo    bar    zap
    Should be equal    ${ret}    foo, bar, zap

Naming without varargs works
    ${ret} =    Args & Varargs    foo    b=bar
    Should be equal    ${ret}     foo, b:bar
    ${ret} =    Args & Varargs    a=1    b=2
    Should be equal    ${ret}     a:1, b:2
    ${ret} =    Args & Varargs    b=B    a=A
    Should be equal    ${ret}     a:A, b:B
    ${ret} =    Args, Varargs & Kwargs    x=1    a=A    b=B    y=2
    Should be equal    ${ret}    a:A, b:B, x:1, y:2

Positional after named 1
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Args & Varargs' got positional argument after named arguments.
    Args & Varargs    foo    b=bar    dar

Positional after named 2
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Args & Varargs' got positional argument after named arguments.
    Args & Varargs    foo    b=bar    @{EMPTY}

Positional after named 3
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Two Args' got positional argument after named arguments.
    Two Args    first=1    oops

Positional after named 4
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Args & Kwargs' got positional argument after named arguments.
    Args & Kwargs    kw=value    ooops

Missing argument 1
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Args & Varargs' missing value for argument 'a'.
    Args & Varargs    b=value

Missing argument 2
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Args & Kwargs' missing value for argument 'a'.
    Args & Kwargs    b=value    kw=value    c=value

Multiple values for argument 1
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Two Args' got multiple values for argument 'first'.
    Two Args    1    first=oops

Multiple values for argument 2
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Args & Varargs' got multiple values for argument 'a'.
    Args & Varargs    A    B   a=ooops

Multiple values for argument 3
    [Documentation]    FAIL Keyword 'DynamicWithKwargs.Args & Kwargs' got multiple values for argument 'a'.
    Args & Kwargs    A    B   a=ooops
