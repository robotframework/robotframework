*** Settings ***
Suite Setup       Fail    Because all tests are skipped or excluded,
Suite Teardown    Fail    suite setup and teardown should not be run.

*** Test Cases ***
Skip using robot:skip
    [Documentation]    SKIP    Test skipped using 'robot:skip' tag.
    [Tags]    robot:skip
    Fail    Should not be run

Skip using --skip
    [Documentation]    SKIP    Test skipped using 'skip-this' tag.
    [Tags]    skip-this
    Fail    Should not be run

Exclude using robot:exclude
    [Tags]    robot:exclude
    Fail    Should not be run
