*** Settings ***
Suite Teardown    Close All Connections
Library           Telnet
Resource          telnet_resource.robot

*** Test Cases ***
Open Connection
    ${index} =    Open Connection    ${HOST}   prompt=xxx
    Should Be Equal    ${index}    ${1}

Close Connection
    [Documentation]    FAIL No connection open
    Read Until    login:
    Write    hello
    Close Connection
    Write    this fails

Closing already closed connection is OK
    Close Connection
    Open Connection    ${HOST}
    Close Connection
    Close Connection
    Sleep    0.1s    Give sockets a little time to *really* close.
    Close Connection

Close All Connections 1
    [Documentation]    FAIL No connection open
    ${index} =    Open Connection    ${HOST}   prompt=xxx
    Should Be Equal    ${index}    ${3}
    Close All Connections
    Write    this fails

Close All Connections 2
    ${index} =    Open Connection    ${HOST}   prompt=xxx
    Should Be Equal    ${index}    ${1}

Switch Connection
    Login And Set Prompt    alias=ORIGINAL
    ${index} =    Login And Set Prompt
    Write    cd /tmp
    Read Until Prompt
    Current Directory Should Be    /tmp
    Switch Connection    ORIGINAL
    Current Directory Should Be    ${HOME}
    Switch Connection    ${index}
    Current Directory Should Be    /tmp


*** Keywords ***
Current Directory Should Be
    [Arguments]    ${expected}
    ${dir} =    Execute Command    pwd
    Should Start With    ${dir}    ${expected}\r\n
