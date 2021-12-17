*** Settings ***
Library     DataDriver
Test Template    Template

*** Test Cases ***
Testcase ${arg9}    Hello

*** Keywords ***
Template
    [Arguments]    ${arg9}
    Log to console    ${arg9}