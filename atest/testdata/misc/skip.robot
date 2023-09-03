*** Test Cases ***
Skip using keyword
    [Documentation]    SKIP    Because we feel like that!
    Log     This is run.
    Skip    Because we feel like that!
    Fail    This is not run.

Skip using keyword in user keyword
    [Documentation]    SKIP    Because we can!
    Log     This is run.
    Skip in user keyword
    Fail    This is not run.

Skip using robot:skip tag
    [Documentation]    SKIP    Test skipped using 'robot:skip' tag.
    [Tags]    robot:skip
    Fail    This is not run.

*** Keywords ***
Skip in user keyword
    Skip    Because we can!
