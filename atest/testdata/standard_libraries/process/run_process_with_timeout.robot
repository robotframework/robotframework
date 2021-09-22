*** Settings ***
Suite Teardown      Remove Files    ${STDOUT}    ${STDERR}
Resource            process_resource.robot

*** Variables ***
@{COMMAND}          python    ${CURDIR}/files/timeout.py
@{QUICK COMMAND}    python    ${CURDIR}/files/timeout.py    0.1

*** Test Cases ***
Finish before timeout
    ${result} =    Run Process    @{QUICK COMMAND}
    Should not be terminated    ${result}

Disable timeout with nONe
    ${result} =    Run Process    @{QUICK COMMAND}    timeout=nONe
    Should not be terminated    ${result}

Disable timeout with empty string
    [Documentation]   Verifying that backwards compatibility is honored
    ${result} =    Run Process    @{QUICK COMMAND}    timeout=
    Should not be terminated    ${result}

Disable timeout with zero
    ${result} =    Run Process    @{QUICK COMMAND}    timeout=0
    Should not be terminated    ${result}

Disable timeout with negative value
    ${result} =    Run Process    @{QUICK COMMAND}    timeout=-1 day
    Should not be terminated    ${result}

On timeout process is terminated by default (w/ default streams)
    ${result} =    Run Process    @{COMMAND}    timeout=200ms
    Should be terminated    ${result}

On timeout process is terminated by default (w/ custom streams)
    ${result} =    Run Process    @{COMMAND}    timeout=200ms
    ...    stdout=${STDOUT}    stderr=${STDERR}
    Should be terminated    ${result}

On timeout process can be killed (w/ default streams)
    ${result} =    Run Process    @{COMMAND}    timeout=0.2    on_timeout=kill
    Should be terminated    ${result}

On timeout process can be killed (w/ custom streams)
    ${result} =    Run Process    @{COMMAND}    timeout=0.2    on_timeout=KiLL
    ...    stdout=${STDOUT}    stderr=${STDERR}
    Should be terminated    ${result}

On timeout process can be left running
    ${result} =    Run Process    @{COMMAND}    timeout=0.2 seconds
    ...    on_timeout=CONTINUE    alias=exceed
    Should Be Equal    ${result}    ${None}
    ${result} =    Wait For Process    handle=exceed
    Should not be terminated    ${result}

*** Keywords ***
Should not be terminated
    [Arguments]    ${result}
    Should Be Equal    ${result.rc}    ${0}
    Should Be Equal    ${result.stdout}    start stdout\nend stdout
    Should Be Equal    ${result.stderr}    start stderr\nend stderr

Should be terminated
    [Arguments]    ${result}
    Should Not Be Equal    ${result.rc}    ${0}
    Should Be Equal    ${result.stdout}    start stdout
    Should Be Equal    ${result.stderr}    start stderr
