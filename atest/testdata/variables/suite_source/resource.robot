*** Settings ***

*** Keywords ***
Check Suite Source In Resource File
    [Arguments]  ${expected suite source}
    Should Be Equal  ${SUITE SOURCE}  ${expected suite source}

