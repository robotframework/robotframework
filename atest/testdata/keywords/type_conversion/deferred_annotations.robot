*** Settings ***
Library           DeferredAnnotations.py

*** Test Cases ***
Annotation created later
    ${value} =    Created later    PEP 649
    Should be equal    ${value}    PEP 649

Annotation not available during execution
    ${result} =    Type checking only    ${1}
    Should Be Equal    ${result}    ${1}

Annotation not available during execution but is known
    ${result} =    Type checking only but known    [1, "2"]
    Should Be Equal    ${result}    ${3}

Non-existing annotation
    ${result} =    Non existing    hello
    Should Be Equal    ${result}    hello
