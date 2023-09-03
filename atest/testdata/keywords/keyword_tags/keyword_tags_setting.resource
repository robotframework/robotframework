*** Settings ***
Keyword Tags        in resource

*** Keywords ***
Keyword without own tags in resource
    No operation

Keyword with own tags in resource
    [Tags]    own
    No operation

Keyword with own tags in documentation in resource
    [Documentation]    Tags: in doc
    No operation
