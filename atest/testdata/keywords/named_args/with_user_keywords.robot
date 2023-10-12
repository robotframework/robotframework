*** Settings ***
Library           helper.py

*** Test Cases ***
Simple Kwarg
    ${ret}=    One Kwarg    kwarg=quux
    Should Be Equal    ${ret}    quux
    ${ret}=    Two Kwargs    first=foo    second=bar
    Should Be Equal    ${ret}    foo, bar
    ${ret}=    Two Kw Args    second=World!    first=Hello
    Should Be Equal    ${ret}    Hello, World!

Kwarg Syntax In Variable Is Ignored
    ${assignment}=    Set Variable    kwarg=value
    ${ret}=    One Kwarg    ${assignment}
    Should Be Equal    ${ret}    kwarg=value

Non-string value in UK kwarg
    ${ret}=    One Kwarg    kwarg=${42}
    Should Be Equal    ${ret}    ${42}

Equals Sign In Kwarg Value
    ${ret}=    One Kwarg    kwarg=bar=quux
    Should Be Equal    ${ret}    bar=quux

Using non-existing kwarg
    ${ret}=    One Kwarg    notkwarg=some value
    Should Be Equal    ${ret}    notkwarg=some value

Escaping Kwarg
    ${ret}=    One Kwarg    kwarg=bar\\=quux
    Should Be Equal    ${ret}    bar\\=quux
    ${ret}=    One Kwarg    kwarg\\=bar=quux
    Should Be Equal    ${ret}    kwarg\\=bar=quux
    ${ret}=    One Kwarg    kwarg\=bar

Mandatory Args Should Be Positioned
    ${ret}=    Mandatory And Kwargs    a    b    c
    Should Be Equal    ${ret}    a, b, c
    ${ret}=    Mandatory And Kwargs    a    c=b
    Should Be Equal    ${ret}    a, c=b, KWARG VALUE

Inside Run Kw
    ${ret}=    Run Keyword    Four Kwargs    foo    bar    d=quux
    Should Be Equal    ${ret}    foo, bar, default, quux

Default value with escaped content
    ${ret}=    Escaped default value    d4=\${nv}
    Should Be Equal    ${ret}    \${notvariable} \\\\ \n${SPACE}\${nv}

Varargs without naming arguments works
    @{ret} =    Named arguments with varargs    foo    bar    dar
    Should be equal    ${ret}[0]    foo
    @{ret} =    Named arguments with varargs    foo    bar=bar    dar
    Should be equal    ${ret}[1]    bar=bar
    @{ret} =    Named arguments with varargs    foo    b\=bar    dar
    Should be equal    ${ret}[1]    b=bar

Naming without the varargs works
    @{ret} =    Named arguments with varargs    foo    b=bar
    Should be equal    ${ret}[1]    bar

Varargs with naming does not work
    [Documentation]    FAIL Keyword 'Named arguments with varargs' got positional argument after named arguments.
    Named arguments with varargs    foo    b=bar    dar

Varargs with naming does not work with empty lists either
    [Documentation]    FAIL Keyword 'Named arguments with varargs' got positional argument after named arguments.
    Named arguments with varargs    foo    b=bar    @{EMPTY}

Named combinations with varargs
    [Template]    Execute working named vararg combination with result
    a, default    a
    a, default    a=a
    a, b          a=a    b=b
    a, b          b=b    a=a
    c=c, d=d      c=c    d=d
    a, b          a      b
    a, b          a      b=b
    a, b, c       a      b      c
    a, b, c=c     a      b      c=c

Non working named combinations with varargs
    [Template]    Execute illegal named vararg combination
    got positional argument after named arguments.    a=a    b
    missing value for argument 'a'.                   b=b
    got positional argument after named arguments.    b=b    b
    got positional argument after named arguments.    a      b=b    c
    got unexpected named argument 'c'.                a      b=b    c=c
    got multiple values for argument 'a'.             a      b      a=a
    got multiple values for argument 'b'.             a      b      b=b
    got multiple values for argument 'a'.             a      a=a
    got multiple values for argument 'a'.             a      b      c      a=a

Named combinations without varargs
    [Template]    Execute working named combination with result
    a, default    a
    a, default    a=a
    a, b          a=a    b=b
    a, b          b=b    a=a
    a, b          a      b
    a, b          a      b=b

Non working named combinations without varargs
    [Template]    Execute illegal named combination
    got positional argument after named arguments.    a=a    b
    missing value for argument 'a'.                   b=b
    got positional argument after named arguments.    b=b    b
    got multiple values for argument 'a'.             a      a=a

Nön äscii named arguments
    ${result} =      Named arguments with nönäscii     nönäscii=pöpipöö
    Should be equal    ${result}     pöpipöö

*** Keywords ***
Execute working named vararg combination with result
    [Arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Mandatory, Named and varargs    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal named vararg combination
    [Arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Mandatory, Named and varargs    @{args}
    Should be equal    ${res}    Keyword 'Mandatory, Named and varargs' ${expected error}

Execute working named combination with result
    [Arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Mandatory and Named    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal named combination
    [Arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Mandatory and Named    @{args}
    Should be equal    ${res}    Keyword 'Mandatory and Named' ${expected error}

Mandatory, Named and varargs
    [Arguments]    ${a}    ${b}=default    @{varargs}
    ${res}=    pretty    ${a}    ${b}    @{varargs}
    RETURN    ${res}

Mandatory and Named
    [Arguments]    ${a}    ${b}=default
    ${res}=    pretty    ${a}    ${b}
    RETURN    ${res}

One Kwarg
    [Arguments]    ${kwarg}=
    RETURN    ${kwarg}

Two Kwargs
    [Arguments]    ${first}=    ${second}=
    RETURN    ${first}, ${second}

Four Kw Args
    [Arguments]    ${a}=default    ${b}=default    ${c}=default    ${d}=default
    RETURN    ${a}, ${b}, ${c}, ${d}

Mandatory And Kwargs
    [Arguments]    ${man1}    ${man2}    ${kwarg}=KWARG VALUE
    RETURN    ${man1}, ${man2}, ${kwarg}

Escaped default value
    [Arguments]    ${d1}=\${notvariable}    ${d2}=\\\\    ${d3}=\n    ${d4}=\t
    RETURN    ${d1} ${d2} ${d3} ${d4}

Named arguments with varargs
    [Arguments]    ${a}=default    ${b}=default    @{varargs}
    RETURN    ${a}    ${b}    @{varargs}

Named arguments with nönäscii
    [Arguments]    ${nönäscii}=
    RETURN       ${nönäscii}
