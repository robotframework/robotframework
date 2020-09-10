*** Settings ***
Suite Teardown  Run Keyword And Warn On Failure  Fail  Expected Warn From Suite Teardown

*** Test Cases ***

Run Keyword And Warn On Failure
    Run Keyword And Warn On Failure  Log  aloha
    Log    This should be executed

Run Keyword And Warn On Failure For Keyword Teardown
    Run Keyword And Warn On Failure    User Keyword With Failing Teardown
    Log  This Should Be Executed

Run User keyword And Warn On Failure
    Run keyword And Warn On Failure    Exception In User Defined Keyword
    Log    This should be executed

Run Keyword And Warn On Failure With Syntax Error
    [Documentation]    FAIL    Keyword 'BuiltIn.No Operation' expected 0 arguments, got 1.
    Run keyword And Warn On Failure    No Operation    illegal argument
    Fail    This Should Not Be Executed!

Run Keyword And Warn On Failure With Failure On Test Teardown
    [Teardown]  Run Keyword And Warn On Failure  Fail    Expected Warn From Test Teardown
    Log  This should Be Executed

*** Keywords ***
User Keyword With Failing Teardown
    No Operation
    [Teardown]    Fail    Expected Warn From User Teardown

Exception In User Defined Keyword
    Fail    Expected Warn In User Keyword
