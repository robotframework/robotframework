*** Settings ***
Test Template       Log

*** Test Cases ***

Default template
    [Documentation]    Log
    Use template from settings table

Overridden template
    [Documentation]    Comment
    [Template]    Comment
    Use my own template

Overridden with empty
    [Template]
    Log  No template

Overridden with NONE
    [Template]    NONE
    Log  No template
