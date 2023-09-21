*** Settings ***
Library           unionsugar.py
Resource          conversion.resource
Force Tags        require-py3.10

*** Test Cases ***
Union
    [Template]    Union of int float and string
    1          1
    2.1        2.1
    ${1}       ${1}
    ${2.1}     ${2.1}
    2hello     2hello
    ${-110}    ${-110}

Union with None and without str
    [Template]    Union with int and None
    1          ${1}
    ${2}       ${2}
    ${None}    ${None}
    NONE       ${None}

Union with None and str
    [Template]    Union with int None and str
    1          1
    NONE       NONE
    ${2}       ${2}
    ${None}    ${None}
    three      three

Union with ABC
    [Template]    Union with ABC
    ${1}     ${1}
    1        ${1}

Union with subscripted generics
    [Template]    Union with subscripted generics
    \[1, 2]        [1, 2]
    ${{[1, 2]}}    [1, 2]
    42             42
    ${42}          42

Union with subscripted generics and str
    [Template]    Union with subscripted generics and str
    \['a', 'b']        "['a', 'b']"
    ${{['a', 'b']}}    ['a', 'b']
    foo                "foo"

Union with TypedDict
    [Template]    Union with TypedDict
    {'x': 1}           {'x': 1}
    NONE               None
    ${NONE}            None

Union with item not liking isinstance
    [Template]    Union with item not liking isinstance
    42                 ${42}
    3.14               ${3.14}

Argument not matching union
    [Template]    Conversion Should Fail
    Union of int and float             not a number    type=integer or float
    Union of int and float             ${NONE}         type=integer or float    arg_type=None
    Union of int and float             ${CUSTOM}       type=integer or float    arg_type=Custom
    Union with int and None            invalid         type=integer or None
    Union with subscripted generics    invalid         type=list[int] or integer

Union with unrecognized type
    ${myobject}=    Create my object
    Custom type in union    my string      str
    Custom type in union    ${myobject}    MyObject
    Custom type in union    ${42}          str
    Custom type in union    ${CUSTOM}      str

Union with only unrecognized types
    ${myobject}=    Create my object
    Only custom types in union    my string      str
    Only custom types in union    ${myobject}    MyObject
    Only custom types in union    ${42}          int
    Only custom types in union    ${CUSTOM}      Custom

Avoid unnecessary conversion
    [Template]    Union With String First
    Hyvä!      Hyvä!
    1          1
    ${1}       1
    None       None
    ${None}    ${None}

Avoid unnecessary conversion with ABC
    [Template]    Union With str and ABC
    Hyvä!                            Hyvä!
    1                                1
    ${1}                             ${1}
    ${{fractions.Fraction(1, 3)}}    ${{fractions.Fraction(1, 3)}}
