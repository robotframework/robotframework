*** Test Cases ***
Fail to pass
    Fail    Pass me!
    Log     I'm run.

Pass to fail
    [Documentation]    FAIL    Ooops!!
    Log     Fail me!
    Log     I'm not run.

Pass to fail without a message
    [Documentation]    FAIL
    Log    Silent fail!
    Log    I'm not run.

Skip to fail
    [Documentation]    FAIL    Failing!
    Skip    Fail me!
    Log     I'm not run.

Fail to skip
    [Documentation]    SKIP    Skipping!
    Fail    Skip me!
    Log     I'm not run.

Not run to fail
    [Documentation]    FAIL    Several failures occurred:
    ...
    ...    1) Ooops!!
    ...
    ...    2) Failing without running!
    Log     Fail me!
    Log     I'm not run.
    Log     Fail me!
    Log     I'm not run.

Pass and fail to not run
    [Documentation]    FAIL    I fail!
    Log     Mark not run!
    Fail    Mark not run!
    Fail    I fail!

Only message
    [Documentation]    FAIL    Changed!
    Fail    Change me!
    Change message

Control structures
    FOR    ${x}    IN RANGE    1000
        Fail    Handled on FOR level.
    END
    WHILE    True
        Fail    Handled on WHILE level.
    END
    IF    True
        Fail    Handled on IF/ELSE ROOT level.
    ELSE
        Log     I'm not run.
    END
    TRY
        Fail    Handled on TRY/EXCEPT ROOT level.
    EXCEPT    No match
        Log     I'm not run.
    END
