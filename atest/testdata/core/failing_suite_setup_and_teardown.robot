*** Settings ***
Suite Setup       Fail    Setup failure\nin two lines
Suite Teardown    Fail    Teardown failure\nin two lines

*** Test Cases ***
Test 1
    [Documentation]    FAIL Parent suite setup failed:
    ...    Setup failure
    ...    in two lines
    ...
    ...    Also parent suite teardown failed:
    ...    Teardown failure
    ...    in two lines
    Fail    This is not executed

Test 2
    [Documentation]    FAIL Parent suite setup failed:
    ...    Setup failure
    ...    in two lines
    ...
    ...    Also parent suite teardown failed:
    ...    Teardown failure
    ...    in two lines
    Fail    This is not executed
