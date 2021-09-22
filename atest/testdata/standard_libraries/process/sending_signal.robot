*** Settings ***
Test Setup        Remove File    ${TEMPFILE}
Suite Teardown    Terminate All Processes
Resource          process_resource.robot

*** Test Cases ***
Sending INT signal
    Killer signal    INT

Sending SIGINT signal
    Killer signal    SIGINT

Sending INT signal as a text number
    Killer signal    2

Sending INT signal as a number
    Killer signal    ${2}

Send other well-known signals
    FOR    ${signal}    IN    TERM    SIGTERM    15    KILL    SIGKILL    ${9}
        Killer signal    ${signal}
    END

By default signal is not sent to process running in shell
    Precondition not OSX
    Start Countdown    shell=yes
    Send Signal To Process    TERM
    Countdown should not have stopped

By default signal is sent only to parent process
    Start Countdown    children=3
    Send Signal To Process    SIGTERM
    Countdown should not have stopped

Signal can be sent to process running in shell
    Killer signal    TERM    shell=True    group=yes

Signal can be sent to child processes
    Killer signal    TERM    children=3    group=${True}

Sending an unknown signal
    [Documentation]    FAIL Unsupported signal 'unknown'.
    Start Python Process    1+1
    Send Signal To Process    unknown

Sending signal to a process with a handle
    ${index} =    Start Countdown
    Send Signal To Process    INT    group=yes    handle=${index}
    Countdown Should Have Stopped    ${index}
    Start Countdown    alias=alias
    Send Signal To Process    TERM    alias
    Countdown Should Have Stopped    alias

Sending signal to a process with a wrong handle
    [Documentation]    FAIL Non-existing index or alias 'unknown'.
    Send Signal To Process    2    handle=unknown

*** Keywords ***
Killer signal
    [Arguments]    ${signal}    ${shell}=False    ${children}=0    ${group}=False
    Start Countdown    alias=${signal}    shell=${shell}    children=${children}
    Send Signal To Process    ${signal}    group=${group}
    Countdown Should Have Stopped    handle=${signal}

Start Countdown
    [Arguments]    ${alias}=    ${shell}=False    ${children}=0
    ${handle} =    Start Process    python    ${COUNTDOWN}    ${TEMPFILE}
    ...    ${children}    alias=${alias}    shell=${shell}
    Wait Until Countdown Started
    [Return]    ${handle}
