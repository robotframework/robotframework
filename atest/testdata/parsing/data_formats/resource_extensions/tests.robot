*** Settings ***
Resource         resource.resource

*** Test Cases ***
Resource with '*.resource' extension
    Keyword in resource.resource
    Keyword in nested.resource
    Should Be Equal    ${RESOURCE}    resource.resource
    Should Be Equal    ${NESTED}      nested.resource
    Log    ${RESOURCE}
    Log    ${NESTED}
