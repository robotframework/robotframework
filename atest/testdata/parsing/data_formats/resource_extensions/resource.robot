*** Settings ***
Resource         nested.resource

*** Variables ***
${ROBOT}      resource.robot

*** Keywords ***
Keyword in resource.robot
    Keyword in nested.resource
    Should Be Equal    ${NESTED}      nested.resource
    Should Be Equal    ${ROBOT}    resource.robot
