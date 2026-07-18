*** Settings ***
Library           Process
Library           Collections
Library           OperatingSystem

*** Variables ***
${SCRIPT}         ${CURDIR}${/}files${/}script.py
${ENCODING SCRIPT}    ${CURDIR}${/}files${/}encoding.py
${COUNTDOWN}      ${CURDIR}${/}files${/}countdown.py
${TEMPFILE}       %{TEMPDIR}${/}terminate-process-temp.txt
${STARTED}        %{TEMPDIR}${/}some-process-started.txt
${STDOUT}         %{TEMPDIR}/process-stdout-file.txt
${STDERR}         %{TEMPDIR}/process-stderr-file.txt
${STDIN}          %{TEMPDIR}/process-stdin-file.txt
${CWD}            %{TEMPDIR}/process-cwd

*** Keywords ***
Some process
    [Arguments]    ${alias}=${null}    ${stderr}=STDOUT
    Remove File    ${STARTED}
    ${handle}=    Start Python Process
    ...    open(r'${STARTED}', 'w', encoding='ASCII').close(); print(input())
    ...    alias=${alias}    stderr=${stderr}    stdin=PIPE
    Wait Until Created    ${STARTED}    timeout=10s
    Process Should Be Running
    RETURN    ${handle}

Stop some process
    [Arguments]    ${handle}=${NONE}    ${message}=
    ${running}=    Is Process Running    ${handle}
    IF    not $running    RETURN
    ${process}=    Get Process Object    ${handle}
    ${stdout}    ${_} =    Call Method    ${process}    communicate    ${message.encode('ASCII') + b'\n'}
    RETURN    ${stdout.decode('ASCII').rstrip()}

Result should equal
    [Arguments]    ${result}    ${stdout}=    ${stderr}=    ${rc}=0
    ...    ${stdout_path}=    ${stderr_path}=
    Should Be Equal    ${result.stdout}    ${stdout}    stdout
    Should Be Equal    ${result.stderr}    ${stderr}    stderr
    Result should match    ${result}    ${stdout}    ${stderr}    ${rc}
    ...    ${stdout_path}    ${stderr_path}

Result should match
    [Arguments]    ${result}    ${stdout}=    ${stderr}=    ${rc}=0
    ...    ${stdout_path}=    ${stderr_path}=
    Should Match    ${result.stdout}    ${stdout}    stdout
    Should Match    ${result.stderr}    ${stderr}    stderr
    Should Be Equal As Integers    ${result.rc}    ${rc}    rc
    ${stdout_path} =    Custom stream should contain    ${stdout_path}    ${result.stdout}
    ${stderr_path} =    Custom stream should contain    ${stderr_path}    ${result.stderr}
    Should Be Equal    ${result.stdout_path}    ${stdout_path}    stdout_path
    Should Be Equal    ${result.stderr_path}    ${stderr_path}    stderr_path

Custom stream should contain
    [Arguments]    ${path}    ${expected}
    IF    not $path    RETURN
    ${path} =    Normalize Path    ${path}
    ${content} =    Get File    ${path}    encoding=CONSOLE
    Should Be Equal    ${content.rstrip()}    ${expected}
    RETURN    ${path}

Script result should equal
    [Documentation]    These are default results by ${SCRIPT}
    [Arguments]    ${result}    ${stdout}=stdout    ${stderr}=stderr    ${rc}=0
    Result should equal    ${result}    ${stdout}    ${stderr}    ${rc}

Start Python Process
    [Arguments]    ${command}    ${alias}=${NONE}    ${stdout}=${NONE}    ${stderr}=${NONE}
    ...    ${stdin}=None    ${shell}=False
    ${handle}=    Start Process    python    -c    ${command}
    ...    alias=${alias}    stdout=${stdout}    stderr=${stderr}    stdin=${stdin}    shell=${shell}
    RETURN    ${handle}

Run Python Process Interactive
    [Arguments]    ${command}=${EMPTY}    ${alias}=${NONE}    ${stdout}=${STDOUT}    ${stderr}=${STDERR}    ${stdin}=PIPE
    ${result}=    Start Process    python    -i    ${command}
    ...    alias=${alias}    stdout=${stdout}    stderr=${stderr}    stdin=${stdin}
    RETURN    ${result}

Run Python Process
    [Arguments]    ${command}    ${alias}=${NONE}    ${stdout}=${NONE}    ${stderr}=${NONE}
    ${result}=    Run Process    python    -c    ${command}
    ...    alias=${alias}    stdout=${stdout}    stderr=${stderr}
    RETURN    ${result}

Safe Remove File
    [Documentation]    Ignore errors caused by process being locked.
    [Arguments]    @{paths}
    Run Keyword And Ignore Error    Remove Files    @{paths}

Safe Remove Directory
    [Arguments]    ${path}
    Run Keyword And Ignore Error    Remove Directory    ${path}    recursive=yep

Check Precondition
    [Arguments]    ${precondition}
    Should Be True    ${precondition}    Precondition '${precondition}' was not true.

Wait until countdown started
    Wait Until Created    ${TEMPFILE}

Countdown should have stopped
    [Arguments]    ${handle}=${None}
    ${result}=    Wait For Process    ${handle}
    Should Not Be Equal    ${result.rc}    ${0}    handle ${handle}
    ${content1} =    Get File    ${TEMPFILE}
    Should Not Contain    ${content1}    BLASTOFF
    Sleep    0.2
    ${content2} =    Get File    ${TEMPFILE}
    Should Be Equal    ${content1}    ${content2}

Countdown should not have stopped
    [Arguments]    ${handle}=${None}
    ${result}=    Wait For Process    ${handle}
    Should Not Be Equal    ${result.rc}    ${0}
    Wait Until Keyword Succeeds    2.2s    0.2s    Blastoff Successful

Blastoff Successful
    ${content} =    Get File    ${TEMPFILE}
    Should End With    ${content}    BLASTOFF

Create environ
    [Arguments]    &{environ}
    ${path} =    Get Environment Variable    PATH    default=.
    ${systemroot} =    Get Environment Variable    SYSTEMROOT    default=.
    ${environ} =    Set To Dictionary    ${environ}    PATH=${path}    SYSTEMROOT=${SYSTEMROOT}
    RETURN    ${environ}
