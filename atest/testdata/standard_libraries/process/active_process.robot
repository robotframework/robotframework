*** Settings ***
Resource          process_resource.robot
Test Teardown     Terminate all processes

*** Test Cases ***
Implicit handle
    Some process
    ${stdout} =    Stop some process    message=42
    Should Be Equal    ${stdout}    42

Explicit handle
    ${handle} =    Some process
    ${stdout} =    Stop some process    ${handle}    43
    Should Be Equal    ${stdout}    43

Alias
    Some process    alias=saila
    ${stdout} =    Stop some process    saila    44
    Should Be Equal    ${stdout}    44

Index
    [Documentation]    Mainly for compatibility with RF < 5.0 when Start Process
    ...                returned process index, not Popen object, as handle.
    Some process
    ${stdout} =    Stop some process    1    45
    Should Be Equal    ${stdout}    45
    Some process
    ${stdout} =    Stop some process    2    46
    Should Be Equal    ${stdout}    46

Implicit handle, explicit handle, alias, and index are equivalent
    ${handle}=    Some process    alias=saila
    ${pid by implicit handle} =    Get process id
    ${pid by explicit handle} =    Get process id    ${handle}
    ${pid by alias} =    Get process id    saila
    ${pid by index} =    Get process id    1
    Should Be Equal    ${pid by implicit handle}    ${pid by explicit handle}
    Should Be Equal    ${pid by implicit handle}    ${pid by alias}
    Should Be Equal    ${pid by implicit handle}    ${pid by index}

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
