*** Settings ***
Library         ${oslib}
Library         ${param}Library  @{args}

*** Variables ***
${oslib}  OperatingSystem
${param}  Parameter
@{args}  myhost  1000

*** Test Cases ***
Verify Library Import With Variable In Name
    Directory Should Not Be Empty    ${CURDIR}
    Directory Should Exist    %{TEMPDIR}

Verify Library Import With List Variable
    ${host}    ${port} =    Parameters
    Should Be Equal    ${host}    myhost
    Should Be Equal    ${port}    1000
