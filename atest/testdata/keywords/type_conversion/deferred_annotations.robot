*** Settings ***
Library    DeferredAnnotations.py

*** Test Cases ***
Deferred evaluation of annotations
    ${value} =    Deferred evaluation of annotations    PEP 649
    Should be equal    ${value}    PEP 649

Type checking annotation
    ${result} =    Type checking annotation    ${1}
    Should Be Equal    ${result}    ${1}

Nonexisting annotation
    ${result} =    Nonexisting annotation    hello
    Should Be Equal    ${result}    hello

Type checking annotation with parameterized generic
    ${result} =    My Sum    [1, "2"]
    Should Be Equal    ${result}    ${3}
