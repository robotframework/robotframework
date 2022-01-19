*** Test Cases ***
Passing test does not initiate exit-on-failure
    No Operation

Skipped test does not initiate exit-on-failure
    [Documentation]    SKIP    testing...
    Skip    testing...

Test skipped in teardown does not initiate exit-on-failure
    [Documentation]    SKIP    testing...
    No Operation
    [Teardown]    Skip    testing...

Skip-on-failure test does not initiate exit-on-failure
    [Documentation]    SKIP
    ...       Test failed but skip-on-failure mode was active and it was marked skipped.
    ...
    ...       Original failure:
    ...       Does not initiate exit-on-failure
    [Tags]    skip-on-failure
    Fail    Does not initiate exit-on-failure

Test skipped-on-failure in teardown does not initiate exit-on-failure
    [Documentation]    SKIP
    ...       Test failed but skip-on-failure mode was active and it was marked skipped.
    ...
    ...       Original failure:
    ...       Teardown failed:
    ...       Does not initiate exit-on-failure
    [Tags]    skip-on-failure
    No Operation
    [Teardown]    Fail    Does not initiate exit-on-failure

Failing test initiates exit-on-failure
    [Documentation]    FAIL Initiates exit-on-failure
    Fail    Initiates exit-on-failure

Not executed
    Fail    Not executed
