*** Settings ***
Library         ParameterLibrary

*** Test Cases ***
Two default parameters
    ${host}    ${port} =    Parameters
    Should Be Equal    ${host}    localhost
    Should Be Equal    ${port}    8080
