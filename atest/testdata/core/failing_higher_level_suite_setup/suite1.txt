*** Settings ***
Suite Setup  Fail  Not Executed

*** Test cases ***
Test 1
    [Documentation]  FAIL Parent suite setup failed:
    ...    Expected failure in higher level setup
    No operation
