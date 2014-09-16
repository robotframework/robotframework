*** Settings ***
Test Setup        Check Precondition         sys.version_info >= (2,6)
Test Teardown     Terminate All Processes    kill=True
Library           Process
Resource          process_resource.robot

*** Test Cases ***
Wait For Process
    ${process} =    Start Python Process    print 'Robot Framework'
    ${result} =    Wait For Process    ${process}
    Process Should Be Stopped    ${process}
    Should Be Equal As Integers    ${result.rc}    0

Wait For Process Timeout
    ${process} =    Start Python Process    while True: pass
    Process Should Be Running    ${process}
    ${result} =    Wait For Process    ${process}    timeout=1s
    Process Should Be Running    ${process}
    Should Be Equal    ${result}    ${NONE}

Wait For Process Terminate On Timeout
    ${process} =   Start Python Process    while True: pass
    Process Should Be Running    ${process}
    ${result} =    Wait For Process    ${process}    timeout=1s    on_timeout=terminate
    Process Should Be Stopped    ${process}
    Should Not Be Equal As Integers    ${result.rc}    0

Wait For Process Kill On Timeout
    ${process} =   Start Python Process    while True: pass
    Process Should Be Running    ${process}
    ${result} =    Wait For Process    ${process}    timeout=1s    on_timeout=kill
    Process Should Be Stopped    ${process}
    Should Not Be Equal As Integers    ${result.rc}    0
