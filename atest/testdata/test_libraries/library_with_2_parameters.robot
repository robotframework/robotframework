*** Settings ***
Library         ParameterLibrary    myhost    1000

*** Test Cases ***
Two set parameters
    ${host}    ${port} =    Parameters
    Should Be Equal    ${host}    myhost
    Should Be Equal    ${port}    1000
