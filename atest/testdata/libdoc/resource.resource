*** Settings ***
Keyword Tags        keyword    tags

*** Keywords ***
Yay, I got new extension!
    [Arguments]    ${arg: int}
    [Documentation]    Yeah!!!
    No operation

Own tags
    [Tags]    own
    No operation

Tags in documentation
    [Documentation]    Tags: own, in doc
    No operation
