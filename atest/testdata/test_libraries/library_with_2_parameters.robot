*** Settings ***
Library         ParameterLibrary  myhost  1000

*** Test Cases ***
Two Set Parameters
    [Documentation]  Checks that parameters can be given to library PASS
    ${host}  ${port} =  parameters
    equals  ${host}  myhost
    equals  ${port}  1000

