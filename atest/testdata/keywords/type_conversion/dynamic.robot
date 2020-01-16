*** Settings ***
Library                Dynamic.py
Library                DynamicJava.java
Resource               conversion.resource

*** Test Cases ***
List of types
    List of types      42                  42

Dict of types
    Dict of types      42                  Decimal(42)

List of aliases
    List of aliases    BÖÖ!!               b'B\\xd6\\xd6!!'

Dict of aliases
    Dict of aliases    {'a': 1, 'b': 2}    {'a': 1, 'b': 2}

Java types
    [Tags]    require-jython
    Java types         42    3.14    [1, 2, 3]
