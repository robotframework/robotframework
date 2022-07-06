*** Settings ***
Suite Setup        Keyword without own tags
Suite Teardown     Keyword with own tags
Keyword Tags       in init

*** Keywords ***
Keyword without own tags
    No operation

Keyword with own tags
    [Tags]    own
    No operation
