*** Settings ***
Library         ParameterLibrary    myhost

*** Test Cases ***
One default and one set parameter
    ${host}    ${port} =    Parameters
    Should Be Equal    ${host}    myhost
    Should Be Equal    ${port}    8080
