*** Settings ***
Library                  KeywordDecoratorWithList.py
Resource                 conversion.resource

*** Test Cases ***
Basics
    Basics    42    3.14    True    2018-08-30    ['foo']

None means no type
    None means no type    1    2    3

Falsy types mean no type
    Falsy types mean no type    1    2    3

NoneType
    NoneType    1    none    3

None as string is None
    NoneType    1    none    3

None in tuple is alias for NoneType
    [Template]    None in tuple is alias for NoneType
    1       None       exp1=1       exp2=None
    ${1}    ${None}    exp1=1       exp2=None
    NONE    none       exp1=None    exp2=None

Less types than arguments is ok
    Less types than arguments is ok    1    2    3

More types than arguments causes error
    [Documentation]    FAIL No keyword with name 'Too many types' found.
    Too many types

Varargs and kwargs
    Varargs and kwargs    1    2    3    4    kw=5

Kwonly
    Kwonly    foo=1    zap=3    bar=2

Kwonly with kwargs
    Kwonly with varargs and kwargs    0    foo=1    zap=3    bar=2    quux=4
