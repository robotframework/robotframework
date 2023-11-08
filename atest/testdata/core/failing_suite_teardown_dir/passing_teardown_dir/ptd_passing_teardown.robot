*** Test Cases ***
PTD PTD Passing
    [Documentation]    FAIL
    ...    Parent suite teardown failed:
    ...    Failure in top level suite teardown
    No Operation

PTD PTD Failing
    [Documentation]    FAIL
    ...    Failure in test
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in top level suite teardown
    Fail    Failure in test
