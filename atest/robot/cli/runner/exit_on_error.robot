*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${MESSAGE}        Error occurred and exit-on-error mode is in use.

*** Test Cases ***
Parsing error
    [Setup]    Run Tests    --exitonerror    misc/pass_and_fail.robot cli/error/parsing_error.robot misc/normal.robot
    Skipped due to error    Pass    Fail    Parsing Error   First One    Second One
    Teardowns not executed    Parsing Error

Import error
    [Setup]    Run Tests    --exitonerror    misc/pass_and_fail.robot cli/error/import_error.robot misc/normal.robot
    Executed normally    Pass    Fail
    Skipped due to error    Import Error   First One    Second One
    Teardowns not executed    Import Error

Parsing error in imported resource
    [Setup]    Run Tests    --exitonerror    misc/pass_and_fail.robot cli/error/resource_error.robot misc/normal.robot
    Executed normally    Pass    Fail
    Skipped due to error    Resource Error   First One    Second One
    Teardowns not executed    Resource Error

Runtime error
    [Setup]    Run Tests    --exitonerror    misc/pass_and_fail.robot cli/error/runtime_error.robot misc/normal.robot
    Executed normally    Pass    Fail    Before Error
    Failed due to error    Runtime Error
    Skipped due to error    After Error   First One    Second One
    Teardowns executed    Runtime Error

With --SkipTeardownOnExit
    [Setup]    Run Tests    --ExitOnError --SkipTeardownOnExit    misc/pass_and_fail.robot cli/error/runtime_error.robot misc/normal.robot
    Executed normally    Pass    Fail    Before Error
    Failed due to error    Runtime Error
    Skipped due to error    After Error   First One    Second One
    Teardowns not executed    Runtime Error

*** Keywords ***
Executed normally
    [Arguments]    @{tests}
    FOR    ${name}    IN    @{tests}
        Check Test Case    ${name}
    END

Failed due to error
    [Arguments]    ${test}
    Check Test Case    ${test}    FAIL    ${MESSAGE}

Skipped due to error
    [Arguments]    @{tests}
    FOR    ${name}    IN    @{tests}
        ${tc} =    Check Test Case    ${name}    FAIL    ${MESSAGE}
        Should Contain    ${tc.tags}    robot:exit
    END

Teardowns not executed
    [Arguments]    ${name}
    ${suite} =    Get Test Suite    ${name}
    Teardown Should Not Be Defined    ${suite}
    ${tc} =    Check Test Case    ${name}    FAIL    ${MESSAGE}
    Teardown Should Not Be Defined    ${tc}

Teardowns executed
    [Arguments]    ${name}
    ${suite} =    Get Test Suite    ${name}
    Should Be Equal    ${suite.teardown.full_name}    BuiltIn.No Operation
    ${tc} =    Check Test Case    ${name}    FAIL    ${MESSAGE}
    Should Be Equal    ${tc.teardown.full_name}    BuiltIn.No Operation
