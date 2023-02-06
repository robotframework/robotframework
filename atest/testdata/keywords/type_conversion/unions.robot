*** Settings ***
Library           unions.py
Resource          conversion.resource

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
    ${2.0}     ${2}
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
    Union with int and None            ${1.1}          type=integer or None     arg_type=float
    Union with subscripted generics    invalid         type=list or integer

Union with unrecognized type
    ${myobject}=    Create my object
    Unrecognized type    my string      str
    Unrecognized type    ${myobject}    MyObject
    Unrecognized type    ${42}          str
    Unrecognized type    ${CUSTOM}      str
    Unrecognized type    ${{type('StrFails', (), {'__str__': lambda self: 1/0})()}}
    ...                  StrFails

Union with only unrecognized types
    ${myobject}=    Create my object
    Only unrecognized types    my string      str
    Only unrecognized types    ${myobject}    MyObject
    Only unrecognized types    ${42}          int
    Only unrecognized types    ${CUSTOM}      Custom

Multiple types using tuple
    [Template]    Tuple of int float and string
    1          1
    2.1        2.1
    ${21.0}    ${21.0}
    2hello     2hello
    ${-110}    ${-110}

Argument not matching tuple types
    [Template]    Conversion Should Fail
    Tuple of int and float    not a number    type=integer or float
    Tuple of int and float    ${NONE}         type=integer or float    arg_type=None
    Tuple of int and float    ${CUSTOM}       type=integer or float    arg_type=Custom

Optional argument
    [Template]    Optional argument
    1          ${1}
    None       ${None}
    ${None}    ${None}

Optional argument with default
    [Template]    Optional argument with default
    1.1        ${1.1}
    ${1}       ${1.0}
    None       ${None}
    ${None}    ${None}
    expected=${None}

Optional string with None default
    [Template]    Optional string with None default
    Hyvä!      Hyvä!
    1          1
    ${1}       1
    None       None
    ${None}    ${None}
    expected=${None}

String with None default
    [Template]    String with None default
    Hyvä!      Hyvä!
    1          1
    ${1}       1
    None       None
    ${None}    ${None}
    expected=${None}

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

Default value type
    [Documentation]    Default value type is used if conversion fails.
    Incompatible default    1      ${1}
    Incompatible default    1.2    ${1.2}

Default value type with unrecognized type
    [Documentation]    Default value type is never used because conversion cannot fail.
    Unrecognized type with incompatible default    1      ${1}
    Unrecognized type with incompatible default    1.2    1.2

Union with invalid types
    [Template]    Union with invalid types
    xxx      xxx
    ${42}    ${42}

Tuple with invalid types
    [Template]    Tuple with invalid types
    xxx      xxx
    ${42}    ${42}

Union without types
    [Template]    Conversion should fail
    Union without types    whatever    error=Cannot have union without types.    type=union
    Empty tuple            ${666}      error=Cannot have union without types.    type=union    arg_type=integer
