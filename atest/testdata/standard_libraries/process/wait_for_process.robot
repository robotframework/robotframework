*** Settings ***
Test Teardown     Terminate All Processes    kill=True
Library           Process
Library           DateTime
Resource          process_resource.robot

*** Test Cases ***
Wait For Process
    ${process} =    Start Python Process    print('Robot Framework')
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

Wait for process uses minimum of timeout or internal timeout for polling
    ${process} =   Start Python Process    while True: pass
    Process Should Be Running    ${process}
    ${start} =    Get Current Date
    Wait For Process    ${process}    0.001
    ${now}=      Get Current Date
    ${result} =   Subtract Date From Date    ${now}    ${start}
    Should be true   ${result} < 0.1   Maximum time of 0.1s exceeded. Took ${result}s.
