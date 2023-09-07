*** Settings ***
Suite Teardown    Fail    Leaf suite failed

*** Test Cases ***
PTD FTD Passing
    [Documentation]    FAIL
    ...    Parent suite teardown failed:
    ...    Leaf suite failed
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in top level suite teardown
    No Operation

PTD FTD Failing
    [Documentation]    FAIL
    ...    Test failed
    ...
    ...    Also parent suite teardown failed:
    ...    Leaf suite failed
    ...
    ...    Also parent suite teardown failed:
    ...    Failure in top level suite teardown
    Fail    Test failed
