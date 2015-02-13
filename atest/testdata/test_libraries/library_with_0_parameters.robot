*** Settings ***
Library         ParameterLibrary

*** Test Cases ***
Two Default Parameters
    ${host}  ${port} =  parameters
    should be equal  ${host}  localhost
    should be equal  ${port}  8080

