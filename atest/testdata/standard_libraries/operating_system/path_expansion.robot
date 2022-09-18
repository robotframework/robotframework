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

Path as `pathlib.Path`
    ${path} =    Normalize Path    ${{pathlib.Path('~/foo')}}
    ${home} =    Get Home
    Should Be Equal    ${path}    ${home}${/}foo
    Directory Should Exist    ${{pathlib.Path('~')}}

*** Keywords ***
Get Home
    [Arguments]    ${case_normalize}=False
    IF    ${WINDOWS}
        ${home} =    Get Environment Variable    USERPROFILE    %{HOMEDRIVE}%{HOMEPATH}
    ELSE
        ${home} =    Get Environment Variable    HOME
    END
    ${home} =    Normalize Path    ${home}    ${case_normalize}
    RETURN    ${home}

Get User
    IF    ${WINDOWS}
        RETURN    %{USERNAME}
    ELSE
        RETURN    %{USER}
    END
