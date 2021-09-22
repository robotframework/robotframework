*** Settings ***
Test Setup        Remove File    ${TEMPFILE}
Test Teardown     Run Keywords
...               Remove File    ${TEMPFILE}    AND
...               Terminate All Processes    kill=True
Library           DateTime
Resource          process_resource.robot

*** Variables ***
${NONTERM}        ${CURDIR}${/}files${/}non_terminable.py

*** Test Cases ***
Terminate process
    ${handle}=    Some process
    ${result} =    Terminate Process    ${handle}
    Process Should Be Stopped    ${handle}
    Should Not Be Equal As Integers     ${result.rc}    0
    Should Be Empty    ${result.stdout}
    Should Be Empty    ${result.stderr}

Kill process
    ${handle}=    Some process
    ${result} =    Terminate Process    ${handle}    kill=true
    Process Should Be Stopped    ${handle}
    Should Not Be Equal As Integers    ${result.rc}    0
    Should Be Empty    ${result.stdout}
    Should Be Empty    ${result.stderr}

Terminate process running on shell
    Check Precondition    os.sep == '/' or hasattr(signal, 'CTRL_BREAK_EVENT')
    Start Process    python    ${COUNTDOWN}    ${TEMPFILE}    shell=True
    Terminate should stop countdown

Kill process running on shell
    Check Precondition    os.sep == '/'
    Start Process    python    ${COUNTDOWN}    ${TEMPFILE}    shell=True
    Terminate should stop countdown    kill=yes

Also child processes are terminated
    Check Precondition    os.sep == '/' or hasattr(signal, 'CTRL_BREAK_EVENT')
    Start Process    python    ${COUNTDOWN}    ${TEMPFILE}    3
    Terminate should stop countdown

Also child processes are killed
    Check Precondition    os.sep == '/'
    Start Process    python    ${COUNTDOWN}    ${TEMPFILE}    3
    Terminate should stop countdown    kill=${True}

Kill process when terminate fails
    Check Precondition    os.sep == '/' or hasattr(signal, 'CTRL_BREAK_EVENT')
    ${lib} =    Get Library Instance    Process
    ${lib.TERMINATE_TIMEOUT} =    Set Variable    ${2}
    ${process} =    Start Process    python    ${NONTERM}    ${TEMPFILE}    stdout=${STDOUT}   stderr=STDOUT
    Wait Until Created    ${TEMPFILE}
    ${result} =    Terminate Process    ${process}    kill=false
    Should Not Be Equal As Integers    ${result.rc}    0
    Should Start With    ${result.stdout}    Starting non-terminable process.

Terminating already terminated process is ok
    ${handle}=    Some process
    Terminate Process    ${handle}
    Terminate Process    ${handle}

Waiting for terminated process is ok
    ${handle}=    Some process
    Terminate Process    ${handle}
    Wait For Process    ${handle}

Terminate all processes
    ${h1}=    Some process
    ${h2}=    Some process
    ${h3}=    Some process
    ${h4}=    Some process
    ${h5}=    Some process
    Sleep    0.1
    ${p1}=    Get Process Object    ${h1}
    ${p2}=    Get Process Object    ${h2}
    ${p3}=    Get Process Object    ${h3}
    ${p4}=    Get Process Object    ${h4}
    ${p5}=    Get Process Object    ${h5}
    FOR    ${process}    IN    ${p1}    ${p2}    ${p3}    ${p4}    ${p5}
        ${poll}=    Call Method    ${process}    poll
        Should Be Equal    ${poll}    ${NONE}
    END
    Switch Process    ${h3}
    Terminate Process    ${h2}
    Terminate All Processes
    Sleep    0.1
    FOR    ${process}    IN    ${p1}    ${p2}    ${p3}    ${p4}    ${p5}
        ${poll}=    Call Method    ${process}    poll
        Should Not Be Equal    ${poll}    ${NONE}
    END

Terminating all empties cache
    Some process
    Terminate All Processes    kill=True
    ${handle} =    Some Process
    Should Be Equal    ${handle}    ${1}

*** Keywords ***
Terminate should stop countdown
    [Arguments]    ${kill}=false
    Wait until countdown started
    Terminate Process    kill=${kill}
    Countdown should have stopped
