*** Settings ***
Resource          process_resource.robot

*** Test Cases ***
Implicit handle
    Some process
    ${stdout} =    Stop some process    message=42
    Should Be Equal    ${stdout}    42

Explicit handle
    ${handle} =    Some process
    ${stdout} =    Stop some process    ${handle}    42
    Should Be Equal    ${stdout}    42

Alias
    Some process    alias=saila
    ${stdout} =    Stop some process    saila    42
    Should Be Equal    ${stdout}    42

Implicit handle, explicit handle, and alias are equivalent
    ${handle}=    Some process    alias=saila
    ${pid by implicit handle} =    Get process id
    ${pid by explicit handle} =    Get process id    ${handle}
    ${pid by alias} =    Get process id    saila
    Should Be Equal    ${pid by implicit handle}    ${pid by explicit handle}
    Should Be Equal    ${pid by implicit handle}    ${pid by alias}

Switching active process
    Some process    one
    Some process    two
    Stop Some Process    one
    Process Should Be Running
    Process Should Be Running    two
    Process Should Be Stopped    one
    Switch Process    one
    Process Should Be Stopped
    Switch Process    two
    Process Should Be Running
    Stop Some Process
    Process Should Be Stopped
    Process Should Be Stopped    two

Run Process does not change active process
    Some process    active
    ${id1}=    Get Process Id
    Run Python Process    1+1
    ${id2}=    Get Process Id
    Should Be Equal    ${id1}    ${id2}
