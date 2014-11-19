*** Settings ***
Test Setup        Check Precondition         sys.version_info >= (2,6)
Test Teardown     Terminate All Processes    kill=True
Library           Process
Library           DateTime
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

Wait for process uses minimum of timeout or internal timeout for polling
    ${process} =   Start Python Process    while True: pass
    Process Should Be Running    ${process}
    Should take less than    0.01   Wait For Process    ${process}    0.001

*** Keywords ***
Should take less than   [Arguments]    ${max time}    ${keyword}   @{arguments}
    ${start}=    Get Current Date
    Run keyword    ${keyword}    @{arguments}
    ${now}=      Get Current Date
    ${result}=   Subtract Date From Date    ${now}    ${start}
    Should be true   ${result} < ${max time}   Maximum time of ${max time} exceeded. Took ${result}
