*** Settings ***
Library         ParameterLibrary

*** Test Cases ***
Two Default Parameters
    ${host}  ${port} =  parameters
    equals  ${host}  localhost
    equals  ${port}  8080

