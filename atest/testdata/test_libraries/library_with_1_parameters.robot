*** Settings ***
Library         ParameterLibrary  myhost

*** Test Cases ***
One Default And One Set Parameter
    [Documentation]  Checks that parameter can be given to library and that one default value is also correct PASS
    ${host}  ${port} =  parameters
    equals  ${host}  myhost
    equals  ${port}  8080

