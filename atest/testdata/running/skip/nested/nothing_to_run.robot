*** Settings ***
Documentation     These tests are not run due to skip in parent suite setup.
...               They should get correct status nevertheless.

*** Test Cases ***
`robot:skip` with skip in directory suite setup
    [Documentation]    SKIP Skipped in parent suite setup:\nAll children must be skipped
    [Tags]    robot:skip
    Fail    Should not be executed!

`--skip` with skip in directory suite setup
    [Documentation]    SKIP Skipped in parent suite setup:\nAll children must be skipped
    [Tags]    skip-this
    Fail    Should not be executed!
