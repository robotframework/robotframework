*** Settings ***
Keyword Tags        in resource

*** Keywords ***
Keyword without own tags in resource
    No operation

Keyword with own tags in resource
    [Tags]    own
    No operation
