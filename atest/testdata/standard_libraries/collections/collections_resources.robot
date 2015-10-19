*** Settings ***
Library           Collections

*** Keywords ***
Compare To Expected String
    [Arguments]    ${list}    ${string}    &{ns}
    ${expected} =    Evaluate    ${string}    namespace=${ns}
    Should Be Equal    ${list}    ${expected}
