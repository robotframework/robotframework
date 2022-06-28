*** Settings ***
Task Tags         file tag

*** Tasks ***
Defaults
    No Operation

Override
    [Tags]        own    tags
    [Setup]       Log    Overriding setup
    [Timeout]     NONE
    No Operation
    [Teardown]    Log    Overriding teardown as well
