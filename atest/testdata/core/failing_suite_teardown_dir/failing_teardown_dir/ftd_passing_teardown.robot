*** Test Cases ***
FTD PTD Passing
    [Documentation]    FAIL
    ...    Parent suite teardown failed:
    ...    Failure in sub suite teardown
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in top level suite teardown
    No Operation

FTD PTD Failing
    [Documentation]    FAIL
    ...    Failure here
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in sub suite teardown
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in top level suite teardown
    Fail    Failure here
