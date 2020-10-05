*** Settings ***
Library                  unions.py
Force Tags               require-py3

*** Test Cases ***
Union testing
     With optional argument  1  ${1}
     With optional argument  None  ${None}

Optional is removed when None is default
     [Documentation]    FAIL ValueError: Argument 'arg' got value 'None' that cannot be converted to float.
     Unescaped optionalism   1.0
     Unescaped optionalism   None

Multitype union works in order
    Union of int float and string   1  ${1}
    Union of int float and string   2.1  ${2.1}
    Union of int float and string   ${21.0}  ${21}
    Union of int float and string   2hello  2hello
    Union of int float and string   ${-110}  ${-110}

Custom type inside of union
    ${myobject}=  Create my object
    Custom type in union  myobject     <class 'str'>
    Custom type in union  ${myobject}  <class 'unions.MyObject'>

Unexpected object is just passed when in union
    ${object}=  Create unexpected object
    Custom type in union  ${object}     <class 'unions.UnexpectedObject'>


