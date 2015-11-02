*** Settings ***
Library           UseBuiltIn.py

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
