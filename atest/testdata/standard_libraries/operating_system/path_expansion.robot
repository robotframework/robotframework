*** Settings ***
Library           OperatingSystem

*** Variables ***
${WINDOWS}        ${/ != '/'}

*** Test Cases ***
Tilde in path
    ${path} =    Normalize Path    ~/foo
    ${home} =    Get Home
    Should Be Equal    ${path}    ${home}${/}foo
    Directory Should Exist    ~

Tilde and username in path
    ${user} =    Get User
    ${path} =    Normalize Path    ~${user}/foo    case_normalize=True
    ${home} =    Get Home    case_normalize=True
    Should Be Equal    ${path}    ${home}${/}foo
    Directory Should Exist    ~${user}

*** Keywords ***
Get Home
    [Arguments]    ${case_normalize}=False
    ${home} =    Run Keyword If    ${WINDOWS}
    ...    Get Windows Home
    ...    ELSE
    ...    Get Posix Home
    ${home} =    Normalize Path    ${home}    ${case_normalize}
    [Return]    ${home}

Get Windows Home
    ${home} =    Get Environment Variable    USERPROFILE    %{HOMEDRIVE}%{HOMEPATH}
    [Return]    ${home}

Get Posix Home
    [Return]    %{HOME}

Get User
    ${user} =    Run Keyword If    ${WINDOWS}
    ...    Get Windows User
    ...    ELSE
    ...    Get Posix User
    [Return]    ${user}

Get Windows User
    [Return]    %{USERNAME}

Get Posix User
    [Return]    %{USER}
