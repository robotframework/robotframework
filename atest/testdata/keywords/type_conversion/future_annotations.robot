*** Settings ***
Library                  FutureAnnotations.py
Resource                 conversion.resource
Force Tags               require-py3.7

*** Test Cases ***
Concrete types
    Concrete types    42    False    [1, 'kaksi']

ABCs
    ABCs    42    {'key': 'value'}

Typing
    Typing    ['foo', 'bar']    [1, 2, 3]

Invalid
    Invalid 1    xxx
    Invalid 2    xxx
