*** Settings ***
Resource         nested.resource

*** Variables ***
${RESOURCE}      resource.resource

*** Keywords ***
Keyword in resource.resource
    Keyword in nested.resource
    Should Be Equal    ${RESOURCE}    resource.resource
    Should Be Equal    ${NESTED}      nested.resource
    Log    ${RESOURCE}
