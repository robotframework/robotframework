*** Settings ***
Resource        variables_for_library_import.robot
Library         ${OS LIB}
Library         ${PARAM}Library    @{ARGS}

*** Test Cases ***
Verify Library Import With Variable In Name
    Directory Should Not Be Empty    ${CURDIR}
    Directory Should Exist    %{TEMPDIR}

Verify Library Import With List Variable
    ${host}    ${port} =    Parameters
    Should Be Equal    ${host}    myhost
    Should Be Equal    ${port}    1000
