*** Test Cases ***
Passing
    No Operation

Passing tests do not initiate exit-on-failure
    No Operation

Skipped on failure
    [Documentation]    SKIP
    ...       Test failed but its tags matched '--SkipOnFailure' and it was marked skipped.
    ...
    ...       Original failure:
    ...       Does not initiate exit-on-failure
    [Tags]    skip-on-failure
    Fail    Does not initiate exit-on-failure

Failing
    [Documentation]    FAIL Initiates exit-on-failure
    Fail    Initiates exit-on-failure

Not executed
    Fail    Not executed
