*** Settings ***
Library           Collections

*** Keywords ***
Compare To Expected String
    [Arguments]    ${list}    ${string}
    ${expected} =    Evaluate    ${string}
    Should Be Equal    ${list}    ${expected}
