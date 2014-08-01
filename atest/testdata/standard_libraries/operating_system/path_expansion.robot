*** Settings ***
Library           OperatingSystem

*** Test Cases ***
Tilde in path
    ${home}=    Get OS Independent Home Path
    ${normalized}=    Normalize Path    ~/foo
    Should Be Equal    ${normalized}    ${home}${/}foo
    Directory Should Exist    ~

Tilde and username in path
    ${user}=    Get OS Independent Username
    ${home}=    Get OS Independent Home Path
    ${normalized}=    Normalize Path    ~${user}/foo
    Should Be Equal    ${normalized}    ${home}${/}foo
    Directory Should Exist    ~${user}

*** Keywords ***
Get OS Independent Username
    ${username}=    Get Environment Variable    USERNAME    NotSet
    ${user}=    Get Environment Variable    USER    ${username}
    [Return]    ${user}

Get OS Independent Home Path
    ${homepath}=    Get Environment Variable    HOMEPATH    NotSet
    ${homedrive}=    Get Environment Variable    HOMEDRIVE    NotSet
    ${home}=    Get Environment Variable    HOME    ${homedrive}${homepath}
    [Return]    ${home}
