*** Settings ***
Library         ParameterLibrary  myhost  1000

*** Test Cases ***
Two Set Parameters
    [Documentation]  Checks that parameters can be given to library PASS
    ${host}  ${port} =  parameters
    should be equal  ${host}  myhost
    should be equal  ${port}  1000

