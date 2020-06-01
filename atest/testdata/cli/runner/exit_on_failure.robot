*** Settings ***
Default Tags        critical

*** Test Cases ***
Passing critical
    No Operation

Passing non-critical
    [Tags]    NONE
    No Operation

Passing tests do not initiate exit-on-failure
    No Operation

Failing non-critical
    [Documentation]    FAIL Not critical
    [Tags]    NONE
    Fail    Not critical

Failing non-critical tests do not initiate exit-on-failure
    No Operation

Failing dynamically non-critical
    [Documentation]    FAIL Criticality removed dynamically
    [Setup]    Remove Tags    critical
    Fail    Criticality removed dynamically

Failing dynamically non-critical tests do not initiate exit-on-failure
    No Operation

Failing critical
    [Documentation]    FAIL Critical - initiates exit-on-failure
    Fail    Critical - initiates exit-on-failure

Skipped
    Fail    Not executed
