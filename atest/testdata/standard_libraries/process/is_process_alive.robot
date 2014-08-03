*** Settings ***
Resource          process_resource.robot

*** Test Cases ***
No Process Should Fail
    Run Keyword And Expect Error    No active process.   Is Process Running

Test Process Should Be Alive
    ${handle}=    Some process
    Process Should Be Running    ${handle}
    ${running} =    Is Process Running
    Should Be Equal    ${running}    ${TRUE}
    Stop some process
    Wait For Process    ${handle}
    ${running} =    Is Process Running
    Should Be Equal    ${running}    ${FALSE}
    Run Keyword And Expect Error    Process is not running.    Process Should Be Running    ${handle}

Test Process Should Be Dead
    ${handle}=    Some process
    Run Keyword And Expect Error    Process is running.    Process Should Be Stopped    ${handle}
    Stop some process
    Wait For Process    ${handle}
    Process Should Be Stopped    ${handle}
