*** Settings ***
Library           unions.py
Resource          conversion.resource
Force Tags        require-py3

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

Argument not matching union
    [Template]    Conversion Should Fail
    Union of int and float     not a number    type=integer or float
    Union of int and float     ${NONE}         type=integer or float    arg_type=None
    Union of int and float     ${{type('Custom', (), {})()}}
    ...                                        type=integer or float    arg_type=Custom
    Union with int and None    invalid         type=integer or None

Union with custom type
    ${myobject}=    Create my object
    ${object}=    Create unexpected object
    Custom type in union    my string      str
    Custom type in union    ${myobject}    MyObject
    Custom type in union    ${object}      UnexpectedObject

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
    Tuple of int and float    ${{type('Custom', (), {})()}}
    ...                                       type=integer or float    arg_type=Custom

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

