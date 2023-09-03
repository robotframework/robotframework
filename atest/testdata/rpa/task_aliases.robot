*** Settings ***
Task Tags               task    tags
Task Setup              Log    Setup has an alias!
Task Teardown           Log    Also teardown has an alias!!
Task Template           Log
Task Timeout            70 seconds
Tesk Setup              Task aliases are included in setting recommendations
Resource                resource_with_invalid_task_settings.robot

*** Variables ***
${TIMEOUT}              TASK

*** Tasks ***
Defaults
    Using default settings

Override
    [Tags]        own    tags
    [Setup]       Log    Overriding setup
    [Template]    NONE
    [Timeout]     NONE
    Log    Overriding settings
    [Teardown]    Log    Overriding teardown as well

Task timeout exceeded
    [Documentation]    FAIL ${TIMEOUT.title()} timeout 99 milliseconds exceeded.
    [Setup]       NONE
    [Timeout]     0.099s
    [Template]    Sleep
    1 second

Invalid task timeout
    [Documentation]    FAIL Setup failed:
    ...    Setting ${TIMEOUT.lower()} timeout failed: Invalid time string 'blaah'.
    [Timeout]     blaah
    No operation
