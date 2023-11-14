*** Settings ***
Library          AsyncDynamic.py

*** Test Cases ***
Dynamic async kw works
    ${result} =    Async Keyword
    Should Be Equal    ${result}    test
