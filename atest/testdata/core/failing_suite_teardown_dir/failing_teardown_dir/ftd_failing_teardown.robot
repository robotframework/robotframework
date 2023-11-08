*** Settings ***
Suite Teardown    Fail    Failure in suite teardown

*** Test Cases ***
FTD FTD Passing
    [Documentation]    FAIL
    ...    Parent suite teardown failed:
    ...    Failure in suite teardown
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in sub suite teardown
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in top level suite teardown
    No Operation

FTD FTD Failing
    [Documentation]    FAIL
    ...    Failure in test
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in suite teardown
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in sub suite teardown
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in top level suite teardown
    Fail    Failure in test
