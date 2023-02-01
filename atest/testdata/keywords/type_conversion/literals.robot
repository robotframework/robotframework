*** Settings ***
Library           literals.py
Resource          conversion.resource

*** Test Cases ***
Literal
    [Template]    Literal of all types
    1          ${1}
    True       ${True}
    a          MyEnum.a    enum=True
    b          b
    None       ${None}
    d          ${{b'd'}}

Nested Literal
    nested literal    1
    Conversion Should Fail    Nested Literal    3    type=Literal[1, 2]

Invalid Literal
    TRY
        Invalid literal    1.1
    EXCEPT      TypeError: 1.1 (float) is not valid as an argument for Literal
        No Operation
    ELSE
        Fail    This should literally never work
    END

External literal
    External literal    1
    Conversion Should Fail    External literal    3    type=Literal[1, 2]

literal string is not an alias
    Conversion Should Fail    Literal string is not an alias    1    type=Literal['int']
    Conversion Should Fail    Literal string is not an alias    ${{int}}    type=Literal['int']    arg_type=integer
    Literal string is not an alias    int

Argument not matching
    [Template]    Conversion Should Fail
    Literal of all types    ${2}    ${2}      type=Literal[1, True, MyEnum.a, 'b', None, b'd']  arg_type=integer
    Literal of all types    ${{type('Custom', (), {})()}}    1
    ...                                       type=Literal[1, True, MyEnum.a, 'b', None, b'd']    arg_type=Custom
    Literal of all types    c    b     type=Literal[1, True, MyEnum.a, 'b', None, b'd']
