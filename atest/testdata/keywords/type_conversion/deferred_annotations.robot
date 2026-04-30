*** Settings ***
Library    DeferredAnnotations.py

*** Test Cases ***
Type checking annotation
    [Tags]    require-py3.14
    ${result} =    Type checking annotation    [1, 2]
    Should Be Equal    ${result}    ${3}

Type checking annotation with mixed types
    [Tags]    require-py3.14
    ${result} =    Type checking annotation    [1, "2"]
    Should Be Equal    ${result}    ${3}

Nonexisting annotation
    [Tags]    require-py3.14
    ${result} =    Nonexisting annotation    hello
    Should Be Equal    ${result}    hello


