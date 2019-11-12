*** Settings ***
Library           KwargsLibrary.py
Library           helper.py
Library           python_library.py
Library           Collections

*** Test Cases ***
Simple Named
    ${ret}=    One Named    named=bar
    Should Be Equal    ${ret}    bar
    ${ret}=    Two Named    fst=bar    snd=quux
    Should Be Equal    ${ret}    bar, quux
    ${ret}=    Two Named    snd=quux    fst=bar
    Should Be Equal    ${ret}    bar, quux

Mandatory And Named As Positional
    ${ret}=    Mandatory And Named    a    b    c
    Should Be Equal    ${ret}    a, b, c

Mandatory And Named As Named
    ${ret}=    Mandatory And Named    a=1    b=2    c=3
    Should Be Equal    ${ret}    1, 2, 3
    ${ret}=    Mandatory And Named    c=3    a=1    b=2
    Should Be Equal    ${ret}    1, 2, 3

Same Argument As Positional And Named Fails
    [Documentation]    FAIL Keyword 'KwargsLibrary.One Named' got multiple values for argument 'named'.
    One Named    positional    named=named

Mandatory, Named And Varargs As Positional
    ${ret}=    Mandatory Named And Varargs    mandatory    d1    d2\=d2
    Should Be Equal    ${ret}    mandatory, d1, d2=d2, []
    ${ret}=    Mandatory Named And Varargs    1    2    3    4    5    6
    Should Be Equal    ${ret}    1, 2, 3, [4, 5, 6]

Naming arguments with varargs is supported when varargs are not used
    ${ret}=    Mandatory Named And Varargs    mandatory    d1    d2=d2
    Should Be Equal    ${ret}    mandatory, d1, d2, []

Naming arguments is not supported when varargs are used
    [Documentation]    FAIL Keyword 'KwargsLibrary.Mandatory Named And Varargs' got positional argument after named arguments.
    Mandatory Named And Varargs    d1    d2=d2    vararg

Naming arguments before possible varargs is not supported with empty lists either
    [Documentation]    FAIL Keyword 'KwargsLibrary.Mandatory Named And Varargs' got positional argument after named arguments.
    Mandatory Named And Varargs    d1    d2=d2    @{EMPTY}

Named Syntax In Variable Is Ignored
    ${assignment}=    Set Variable    named=value
    ${ret}=    One Named    ${assignment}
    Should Be Equal    ${ret}    named=value

Non-string named value
    ${ret}=    One Named    named=${42}
    Should Be Equal    ${ret}    ${42}

Equals Sign In Named Value
    ${ret}=    One Named    named=bar=quux
    Should Be Equal    ${ret}    bar=quux
    ${ret}=    One Named    named===value
    Should Be Equal    ${ret}    ==value

Non-existing argument does not trigger named usage
    ${ret}=    One Named    notnamed=value
    Should Be Equal    ${ret}    notnamed=value
    ${ret}=    One Named    ä=ö
    Should Be Equal    ${ret}    ä=ö

Run Keyword's own named arguments are not resolved
    [Documentation]    FAIL No keyword with name 'name=No Operation' found.
    Run Keyword    name=No Operation

Inside Run Keyword named arguments are resolved
    ${ret}=    Run Keyword    Four Named    foo    d=quux    b=kääx
    Should Be Equal    ${ret}    foo, kääx, None, quux

Named combinations with varargs
    [Template]    Execute working named vararg combination with result
    a, default         a
    a, default         a=a
    a, b               a=a    b=b
    a, b               b=b    a=a
    c=c, d=d           c=c    d=d
    a, b               a      b
    a, b               a      b=b
    a, b, c            a      b       c
    a, 2 (int), c=c    a      ${2}    c=c

Kwargs alone
    ${result} =    Lib Kwargs
    Should Be Equal    ${result}    ${EMPTY}
    ${result} =    Lib Kwargs    foo=1    bar=${2}
    Should Be Equal    ${result}    bar:2 (int), foo:1

Kwargs with escaped equal sign 1
    ${result} =    Lib Kwargs    a\=b=c=d    \===
    Should Be Equal    ${result}    =:=, a=b:c=d
    ${result} =    Lib Kwargs    1\\=x\=y    2\=x\\=y    3\\\\\=x\\\\=y
    Should Be Equal    ${result}    1\\:x=y, 2=x\\:y, 3\\\\=x\\\\:y

Kwargs with escaped equal sign 2
    [Documentation]    FAIL Keyword 'python_library.Lib Kwargs' expected 0 non-named arguments, got 1.
    Lib Kwargs    a\=b\\\=c\\\\\=d\\\\\\\=e

Kwargs with positional and named
    ${result} =    Lib Mandatory Named And Kwargs    mandatory
    Should Be Equal    ${result}    mandatory, 2 (int)
    ${result} =    Lib Mandatory Named And Kwargs    mandatory    optional
    Should Be Equal    ${result}    mandatory, optional
    ${result} =    Lib Mandatory Named And Kwargs    mandatory    b=optional
    Should Be Equal    ${result}    mandatory, optional
    ${result} =    Lib Mandatory Named And Kwargs    mandatory    c=3    d=4
    Should Be Equal    ${result}    mandatory, 2 (int), c:3, d:4
    ${result} =    Lib Mandatory Named And Kwargs    mandatory    optional    c=3
    Should Be Equal    ${result}    mandatory, optional, c:3
    ${result} =    Lib Mandatory Named And Kwargs    b=2    c=3    a=1    d=4
    Should Be Equal    ${result}    1, 2 (int), c:3, d:4

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
    got multiple values for argument 'a'.             a      b      c    a=a

Non working combinations with kwargs
    [Template]    Execute illegal combinations with kwargs
    expected 1 to 2 non-named arguments, got 0.
    missing value for argument 'a'.                   b=2
    missing value for argument 'a'.                   b=2    c=3    d=4
    got multiple values for argument 'a'.             a      a=a
    got multiple values for argument 'a'.             a      b      a=a
    got multiple values for argument 'a'.             a      b=b    a=a
    expected 1 to 2 non-named arguments, got 3.       1      2      3

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
    got multiple values for argument 'a'.             a      b      a=a

Working combinations with all argument types
    [Template]    Execute working combinations with everything
    a, default                  a
    a, default                  a=a
    a, b                        a      b
    a, b                        a      b=b
    a, default, d1:d1           a      d1=d1
    a, b                        a=a    b=b
    a, default, d1:d1           a=a    d1=d1
    a, b, c1                    a      b        c1
    a, b, c1, d1:d1             a      b        c1       d1=d1
    a, default, d1:d1, d2:d2    a      d1=d1    d2=d2

Test escaping with all argument types
    [Template]    Execute working combinations with everything
    # double escaping because of template
    a, default, b=bar:foo      a        b\\=bar=foo
    a, b=bar=foo               a        b\\=bar\\=foo
    a, foo=bar                 a        b=foo\\=bar
    a, default, foo:foo=bar    a        foo=foo\\=bar
    a=a, b=b                   a\\=a    b\\=b

Illegal combinations with all argument types
    [Template]    Execute illegal combinations with everything
    expected at least 1 non-named argument, got 0.      d1=d
    got multiple values for argument 'a'.               a      a=a
    got multiple values for argument 'a'.               a      b       a=a
    got multiple values for argument 'a'.               a      b=b     a=a
    got positional argument after named arguments.      a=a    b
    got multiple values for argument 'b'.               a      b       b=b
    got multiple values for argument 'a'.               a      b       a=a
    got multiple values for argument 'a'.               a      b       c1      a=a
    got positional argument after named arguments.      a=a    b=b     d=d     foo

Multiple named with same name is allowed and last has precedence
    [Setup]    Set Test Variable    ${b}    b
    [Template]    Execute working combinations with everything
    c, default    a=a    a=b       a=c
    a, 3          a      b=1       b=2    ${b}=3
    b, 3, c:2     a=a    ${b}=1    c=1    ${b}=2    c=2    b=3    a=${b}

List variable with multiple values for same variable
    [Documentation]    FAIL Keyword 'python_library.Lib Mandatory And Named 2' got multiple values for argument 'b'.
    @{foo} =    Create list    a    b
    Lib mandatory and named 2    @{foo}    b=given second time

Nön äscii allowed in keyword argument names
    ${result} =  lib_kwargs    äö=böö       官话=官话
    Should be equal   ${result}  äö:böö, 官话:官话

Empty string is allowed in kwargs names
    ${res} =    Lib Mandatory Named varargs and kwargs    a    b    =whut
    Should be equal    a, b, :whut    ${res}

Dict is not converted to kwargs
    [Documentation]    FAIL Keyword 'python_library.Lib Kwargs' expected 0 non-named arguments, got 1.
    ${dict} =    Create Dictionary   a=1    b=2
    lib_kwargs    ${dict}

*** Keywords ***
Execute working combinations with everything
    [Arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Lib Mandatory Named varargs and kwargs    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal combinations with everything
    [Arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Lib Mandatory Named varargs and kwargs    @{args}
    Should be equal    ${res}    Keyword 'python_library.Lib Mandatory Named Varargs And Kwargs' ${expected error}

Execute working named vararg combination with result
    [Arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Lib Mandatory Named and varargs    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal named vararg combination
    [Arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Lib Mandatory Named and varargs    @{args}
    Should be equal    ${res}    Keyword 'python_library.Lib Mandatory Named And Varargs' ${expected error}

Execute illegal combinations with kwargs
    [Arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Lib Mandatory Named and Kwargs    @{args}
    Should be equal    ${res}    Keyword 'python_library.Lib Mandatory Named And Kwargs' ${expected error}

Execute working named combination with result
    [Arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Lib Mandatory and Named    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal named combination
    [Arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Lib Mandatory and Named    @{args}
    Should be equal    ${res}    Keyword 'python_library.Lib Mandatory And Named' ${expected error}
