*** Settings ***
Library    DynamicLibraryWithKwargsSupport.py
Library    helper.py

*** Test Cases ***
Named combinations with kwargs
    [template]    Execute working named kwarg combination with result
    a                    a
    a                    a=a
    a, b                 a=a    b=b
    a, b                 b=b    a=a
    a, b, c:c            c=c    b=b    a=a
    a, c:c, d:d          a      c=c    d=d
    a, b, c:c, d:d       a      c=c    d=d    b=b
    a, b                 a      b
    a, b                 a      b=b
    a, b, c:c            a      b      c=c
    a, b, c:c            a      b=b    c=c

Non working named combinations with kwargs
    [template]    Execute illegal named kwarg combination
    got positional argument after named arguments.    a=a    b
    missing value for argument 'a'.                   b=b
    got positional argument after named arguments.    b=b    b
    got positional argument after named arguments.    a      b=b    c
    got multiple values for argument 'a'.             a      b      a=a
    got multiple values for argument 'b'.             a      b      b=b
    expected 1 to 2 non-keyword arguments, got 3.     a      b      c
    got multiple values for argument 'a'.             a      a=a

Named combinations with varargs and kwargs
    [template]    Execute working named vararg and kwarg combination with result
    a                    a
    a                    a=a
    a, b                 a=a    b=b
    a, b                 b=b    a=a
    a, b, c:c            c=c    b=b    a=a
    a, c:c, d:d          a      c=c    d=d
    a, b                 a      b
    a, b                 a      b=b
    a, b, c              a      b      c
    a, b, c:c            a      b      c=c
    a, b, c:c            a      b=b    c=c
    a, b, c, d:d         a      b      c      d=d

Non working named combinations with varargs and kwargs
    [template]    Execute illegal named vararg and kwarg combination
    got positional argument after named arguments.    a=a    b
    missing value for argument 'a'.                   b=b
    got positional argument after named arguments.    b=b    b
    got positional argument after named arguments.    a      b=b    c
    got multiple values for argument 'a'.             a      b      a=a
    got multiple values for argument 'b'.             a      b      b=b
    got multiple values for argument 'a'.             a      a=a
    got multiple values for argument 'a'.             a      b      c      a=a
    got multiple values for argument 'a'.             a      b      c=c    a=a
    got multiple values for argument 'b'.             a      b      c=c    b=b

Multiple named with same name is allowed and last has precedence 1
    [setup]    Set Test Variable    ${c}    c
    [template]    Execute working named kwarg combination with result
    a, b, c:e          a    c=c       b=b       c=d       c=e
    a, c:2, d:3        a    c=1       d=1       d=2       d=3       c=2
    a, c:5             a    ${c}=1    ${c}=2    ${c}=3    ${c}=4    c=5
    a, c:5             a    c=1       c=2       c=3       c=4       ${c.lower()}=5

Multiple named with same name is allowed and last has precedence 2
    [setup]    Set Test Variable    ${c}    c
    [template]    Execute working named vararg and kwarg combination with result
    a, b, c:d          a    b      c=c    c=d
    a, c:2, d:3        a    c=1    d=1    d=2    c=2    d=3
    a, c:5             a    ${c}=1    ${c}=2    ${c}=3    ${c}=4    c=5
    a, c:5             a    c=1       c=2       c=3       ${c}=4    ${c + '${TESTNAME}'[${100}:]}=5

*** Keywords ***
Execute working named kwarg combination with result
    [arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Mandatory, Named And Kwargs    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal named kwarg combination
    [arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Mandatory, Named And Kwargs    @{args}
    Should be equal    ${res}    Keyword '${DynamicLibrary}.Mandatory, Named And Kwargs' ${expected error}

Execute working named vararg and kwarg combination with result
    [arguments]    ${expected}    @{args}
    ${res} =    Get result or error    Mandatory, Named, Varargs And Kwargs    @{args}
    Should be equal    ${expected}    ${res}

Execute illegal named vararg and kwarg combination
    [arguments]    ${expected error}    @{args}
    ${res} =    Get result or error    Mandatory, Named, Varargs And Kwargs    @{args}
    Should be equal    ${res}    Keyword '${DynamicLibrary}.Mandatory, Named, Varargs And Kwargs' ${expected error}
