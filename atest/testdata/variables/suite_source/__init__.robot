*** Settings ***
Suite Setup     Check Suite Source In Resource File  ${CURDIR}
Suite Teardown  Check Suite Source  ${CURDIR}
Resource        resource.robot

*** Keywords ***
Check Suite Source
    [Arguments]  ${expected suite source}
    Should Be Equal  ${SUITE SOURCE}  ${expected suite source}

