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

Less types than arguments is ok
    Less types than arguments is ok    1    2    3

More types than arguments causes error
    [Documentation]    FAIL No keyword with name 'Too many types' found.
    Too many types

Varargs and kwargs
    Varargs and kwargs    1    2    3    4    kw=5

Kwonly
    [Tags]    require-py3
    Kwonly    foo=1    zap=3    bar=2

Kwonly with kwargs
    [Tags]    require-py3
    Kwonly with varargs and kwargs    0    foo=1    zap=3    bar=2    quux=4

