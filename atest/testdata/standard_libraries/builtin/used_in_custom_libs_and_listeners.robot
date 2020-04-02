*** Settings ***
Test Setup        Set Log Level    INFO
Library           UseBuiltIn.py
Resource          UseBuiltInResource.robot

*** Test Cases ***
Keywords Using BuiltIn
    Log Debug Message
    ${name} =    Get Test Name
    Should Be Equal    ${name}    ${TESTNAME}
    Set Secret Variable
    Should Be Equal    ${SECRET}    *****
    Variable Should Not Exist    ${SET BY LISTENER}

Listener Using BuiltIn
    Should Be Equal    ${SET BY LISTENER}    quux

Use 'Run Keyword' with non-Unicode values
    Use Run Keyword with non Unicode values

Use BuiltIn keywords with timeouts
    [Timeout]    1 day
    Log Debug Message
    Set Secret Variable
    Should Be Equal    ${secret}    *****
    Use Run Keyword with non Unicode values

User keyword used via 'Run Keyword'
    User Keyword via Run Keyword

User keyword used via 'Run Keyword' with timeout and trace level
    [Setup]    Set Log Level    TRACE
    [Timeout]    1 day
    User Keyword via Run Keyword
