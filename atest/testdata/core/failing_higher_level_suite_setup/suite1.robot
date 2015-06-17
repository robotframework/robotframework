*** Settings ***
Suite Setup       Fail    Not Executed

*** Test Cases ***
Test 1
    [Documentation]    FAIL Parent suite setup failed:
    ...    Expected failure in higher level setup
    No Operation
