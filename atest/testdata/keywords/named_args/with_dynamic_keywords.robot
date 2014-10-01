*** Settings ***
Library    ${DynamicLibrary}.py
Library    helper.py

*** Variables ***
${DynamicLibrary}    DynamicLibrary

*** Test Cases ***
Kwarg Syntax In Variable Is Ignored
    ${assignment}=    Set Variable    kwarg=value
    ${ret}=    One Kwarg returned    ${assignment}
    Should Be Equal    ${ret}    kwarg=value

Non-string value in UK kwarg
    ${ret}=    One Kwarg returned    kwarg=${42}
    Should Be Equal    ${ret}    ${42}

Equals Sign In Kwarg Value
    ${ret}=    One Kwarg returned    kwarg=bar=quux
    Should Be Equal    ${ret}    bar=quux

Using non-existing kwarg
    ${ret}=    One Kwarg returned    notkwarg=some value
    Should Be Equal    ${ret}    notkwarg=some value

Escaping Kwarg
    ${ret}=    One Kwarg returned    kwarg=bar\\=quux
    Should Be Equal    ${ret}    bar\\=quux
    ${ret}=    One Kwarg returned    kwarg\\=bar=quux
    Should Be Equal    ${ret}    kwarg\\=bar=quux
    ${ret}=    One Kwarg returned    kwarg\=bar

Mandatory Args Should Be Positioned
    ${ret}=    Mandatory And Kwargs    a    b    c
    Should Be Equal    ${ret}    a, b, c
    ${ret}=    Mandatory And Kwargs    a    c=b
    Should Be Equal    ${ret}    a, c=b

Inside Run Kw
    ${ret}=    Run Keyword    Four Kwargs    foo    bar    d=quux
    Should Be Equal    ${ret}    foo, bar, default, quux

Default value with escaped content
    ${ret}=    Escaped default value    d4=\${nv}
    Should Be Equal    ${ret}    \${notvariable}, \\\\, \n, \${nv}

Varargs without naming arguments works
    ${ret} =    Named arguments with varargs    foo    bar    dar
    Should be equal    ${ret}     foo, bar, dar
    ${ret} =    Named arguments with varargs    foo    bar=bar    dar
    Should be equal    ${ret}     foo, bar=bar, dar
    ${ret} =    Named arguments with varargs    foo    b\=bar    dar
    Should be equal    ${ret}     foo, b=bar, dar

Naming without the varargs works
    ${ret} =    Named arguments with varargs    foo    b=bar
    Should be equal    ${ret}     foo, bar

Varargs with naming does not work
    [documentation]    FAIL    Keyword '${DynamicLibrary}.Named Arguments With Varargs' got positional argument after named arguments.
    Named arguments with varargs    foo    b=bar    dar

Varargs with naming does not work with empty lists either
    [documentation]    FAIL    Keyword '${DynamicLibrary}.Named Arguments With Varargs' got positional argument after named arguments.
    Named arguments with varargs    foo    b=bar    @{EMPTY}

Named combinations with varargs
    [template]    Execute working named vararg combination with result
    a                    a
    a                    a=a
    a, b                 a=a    b=b
    a, b                 b=b    a=a
    c=c, d=d             c=c    d=d
    a, b                 a      b
    a, b                 a      b=b
    a, b, c              a      b      c
    a, b, c=c            a      b      c=c

Non working named combinations with varargs
    [template]    Execute illegal named vararg combination
    got positional argument after named arguments.    a=a    b
    missing value for argument 'a'.                   b=b
    got positional argument after named arguments.    b=b    b
    got positional argument after named arguments.    a      b=b    c
    got multiple values for argument 'a'.             a      b      a=a
    got multiple values for argument 'b'.             a      b      b=b
    got multiple values for argument 'a'.             a      a=a
    got multiple values for argument 'a'.             a      b      c      a=a

Named arguments are set defaults only when needed
    [template]    Execute working named combination with result
    1             1
    1             a=1
    1, 2          a=1    b=2
    1, 2          b=2    a=1
    a, 2          b=2
    1, b, 3       1      c=3

Non working named combinations without varargs
    [template]    Execute illegal named combination
    got positional argument after named arguments.    a=a    b
    missing value for argument 'a'.                   b=b
    got positional argument after named arguments.    b=b    b
    got multiple values for argument 'a'.             a      a=a
    got multiple values for argument 'a'.             a      b      a=a
    got multiple values for argument 'a'.             a      b=b    a=a

Nön äscii named arguments
    ${result} =     Nön äscii named args   官话=官话     nönäscii=nönäscii
    Should be equal      ${result}      nönäscii, 官话

*** Keywords ***
Execute working named vararg combination with result
    [arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Mandatory, Named And Varargs    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal named vararg combination
    [arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Mandatory, Named And Varargs    @{args}
    Should be equal    ${res}    Keyword '${DynamicLibrary}.Mandatory, Named And Varargs' ${expected error}

Execute working named combination with result
    [arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Three named    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal named combination
    [arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Mandatory And Named    @{args}
    Should be equal    ${res}    Keyword '${DynamicLibrary}.Mandatory And Named' ${expected error}
