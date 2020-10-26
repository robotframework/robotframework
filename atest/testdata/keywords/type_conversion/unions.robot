*** Settings ***
Library           unions.py
Resource          conversion.resource
Force Tags        require-py3

*** Test Cases ***
Union
    [Template]    Union of int float and string
    1          ${1}
    2.1        ${2.1}
    ${21.0}    ${21}
    2hello     2hello
    ${-110}    ${-110}

Union with None
    [Template]    Union with None
    1          ${1}
    ${2}       ${2}
    ${None}    ${None}
    NONE       ${None}

Union with None and string
    [Template]    Union with None and str
    1          ${1}
    ${2}       ${2}
    three      three
    ${None}    ${None}
    NONE       ${None}

Argument not matching union
    [Template]    Conversion Should Fail
    Union of int and float    not a number    type=integer or float
    Union of int and float    ${NONE}         type=integer or float    arg_type=None
    Union of int and float    ${{type('Custom', (), {})()}}
    ...                                       type=integer or float    arg_type=Custom
    Union with None           invalid         type=integer or None

Union with custom type
    ${myobject}=    Create my object
    ${object}=    Create unexpected object
    Custom type in union    my string      str
    Custom type in union    ${myobject}    MyObject
    Custom type in union    ${object}      UnexpectedObject

Optional argument
    [Template]    Optional argument
    1       ${1}
    None    ${None}

Optional argument with default
    [Template]    Optional argument with default
    1       ${1}
    None    ${None}
