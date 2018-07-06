*** Variables ***
${NESTED}      nested.resource

*** Keywords ***
Keyword in nested.resource
    Should Be Equal    ${NESTED}    nested.resource
    Log    ${NESTED}
