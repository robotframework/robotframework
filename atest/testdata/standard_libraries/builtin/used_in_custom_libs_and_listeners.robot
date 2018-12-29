*** Settings ***
Library           UseBuiltIn.py
Test Setup        Set Log Level    INFO

*** Test Cases ***
Keywords Using BuiltIn
    Log Debug Message
    ${name} =    Get Test Name
    Should Be Equal    ${name}    ${TESTNAME}
    Set Secret Variable
    Should Be Equal    ${secret}    *****
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
