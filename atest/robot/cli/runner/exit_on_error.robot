*** Settings ***
Force Tags        pybot    jybot    regression
Resource          atest_resource.robot

*** Variables ***
${MESSAGE}        Error occurred and exit-on-error mode is in use.

*** Test Cases ***
Error during parsing
    [Setup]    Run Tests    --exitonerror    misc/pass_and_fail.robot
    ...    cli/error/parsing_error.robot    misc/normal.robot
    Failed due to error    Pass    Fail    Parsing Error   First One    Second One
    Teardowns not executed    Parsing Error

Error in imports
    [Setup]    Run Tests    --exitonerror    misc/pass_and_fail.robot
    ...    cli/error/import_error.robot    misc/normal.robot
    Executed normally    Pass    Fail
    Failed due to error    Import Error   First One    Second One
    Teardowns not executed    Import Error

Error during execution
    [Setup]    Run Tests    --exitonerror    misc/pass_and_fail.robot
    ...    cli/error/runtime_error.robot    misc/normal.robot
    Executed normally    Pass    Fail    Before Error
    Failed due to error    Runtime Error    After Error   First One    Second One
    Teardowns executed    Runtime Error

With --SkipTeardownOnExit
    [Setup]    Run Tests    --ExitOnError --SkipTeardownOnExit    misc/pass_and_fail.robot
    ...    cli/error/runtime_error.robot    misc/normal.robot
    Executed normally    Pass    Fail    Before Error
    Failed due to error    Runtime Error    After Error   First One    Second One
    Teardowns not executed    Runtime Error

*** Keywords ***
Executed normally
    [Arguments]    @{tests}
    :FOR    ${name}    IN    @{tests}
    \    Check Test Case    ${name}

Failed due to error
    [Arguments]    @{tests}
    :FOR    ${name}    IN    @{tests}
    \    Check Test Case    ${name}    FAIL    ${MESSAGE}

Teardowns not executed
    [Arguments]    ${name}
    ${suite} =    Get Test Suite    ${name}
    Should Be Equal    ${suite.teardown}    ${None}
    ${tc} =    Check Test Case    ${name}    FAIL    ${MESSAGE}
    Should Be Equal    ${tc.teardown}    ${None}

Teardowns executed
    [Arguments]    ${name}
    ${suite} =    Get Test Suite    ${name}
    Should Be Equal    ${suite.teardown.name}    BuiltIn.No Operation
    ${tc} =    Check Test Case    ${name}    FAIL    ${MESSAGE}
    Should Be Equal    ${tc.teardown.name}    BuiltIn.No Operation
