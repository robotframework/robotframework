*** Settings ***
Suite Setup       Fail    Because all tests are skipped
Suite Teardown    Fail    these should not be run

*** Test Cases ***
Skip using robot:skip
    [Documentation]    SKIP    Test skipped using 'robot:skip' tag.
    [Tags]    robot:skip
    Fail    Should not be run

Skip using --skip
    [Documentation]    SKIP    Test skipped using '--skip' command line option.
    [Tags]    skip-this
    Fail    Should not be run

Exclude using robot:exclude
    [Tags]    robot:exclude
    Fail    Should not be run
