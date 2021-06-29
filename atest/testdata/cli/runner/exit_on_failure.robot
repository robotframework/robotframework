*** Test Cases ***
Passing tests do not initiate exit-on-failure
    No Operation

Skipped tests do not initiate exit-on-failure
    [Documentation]    SKIP    testing...
    Skip    testing...

Skip-on-failure tests do not initiate exit-on-failure
    [Documentation]    SKIP
    ...       Test failed but its tags matched '--SkipOnFailure' and it was marked skipped.
    ...
    ...       Original failure:
    ...       Does not initiate exit-on-failure
    [Tags]    skip-on-failure
    Fail    Does not initiate exit-on-failure

Failing tests initiate exit-on-failure
    [Documentation]    FAIL Initiates exit-on-failure
    Fail    Initiates exit-on-failure

Not executed
    Fail    Not executed
