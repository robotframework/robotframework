*** Settings ***
Resource          process_resource.robot
Suite Teardown    Remove Files    ${STDOUT}    ${STDERR}

*** Variables ***
@{COMMAND}        python    ${CURDIR}/files/timeout.py

*** Test Cases ***
Finish before timeout
    ${result} =    Run Process    @{COMMAND}
    Should not be terminated    ${result}

On timeout process is terminated by default (w/ default streams)
    ${result} =    Run Process    @{COMMAND}    timeout=200ms
    Should be terminated    ${result}    empty output=os.sep == '/' and sys.platform.startswith('java')

On timeout process is terminated by default (w/ custom streams)
    ${result} =    Run Process    @{COMMAND}    timeout=200ms
    ...    stdout=${STDOUT}    stderr=${STDERR}
    Should be terminated    ${result}

On timeout process can be killed (w/ default streams)
    ${result} =    Run Process    @{COMMAND}    timeout=0.2    on_timeout=kill
    Should be terminated    ${result}    empty output=os.sep == '/' and sys.platform.startswith('java1.8')

On timeout process can be killed (w/ custom streams)
    ${result} =    Run Process    @{COMMAND}    timeout=0.2    on_timeout=KiLL
    ...    stdout=${STDOUT}    stderr=${STDERR}
    Should be terminated    ${result}

On timeout process can be left running
    ${result} =    Run Process    @{COMMAND}    timeout=0.2
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
    [Arguments]    ${result}    ${empty output}=False
    Should Not Be Equal    ${result.rc}    ${0}
    ${expected stdout}    ${expected stderr} =
    ...    Run Keyword If    not (${empty output})
    ...    Create List    start stdout    start stderr
    ...    ELSE
    ...    Create List    ${EMPTY}    ${EMPTY}
    Should Be Equal    ${result.stdout}    ${expected stdout}
    Should Be Equal    ${result.stderr}    ${expected stderr}
