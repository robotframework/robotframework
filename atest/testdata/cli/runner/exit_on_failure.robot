*** Settings ***
Default Tags        critical

*** Test Cases ***
Passing
    No Operation

Passing tests do not initiate exit-on-failure
    No Operation

Failing
    [Documentation]    FAIL initiates exit-on-failure
    Fail    initiates exit-on-failure

Skipped
    Fail    Not executed
