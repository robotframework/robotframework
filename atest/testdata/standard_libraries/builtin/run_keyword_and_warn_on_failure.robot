*** Settings ***
Suite Teardown    Run Keyword And Warn On Failure    Fail    Expected Warn From Suite Teardown

*** Test Cases ***
Run Keyword And Warn On Failure
    [Documentation]    PASS
    Run Keyword And Warn On Failure    FAIL    Expected Warn
    Log    This should be executed

Run Keyword And Warn On Failure For Keyword Teardown
    [Documentation]    PASS
    Run Keyword And Warn On Failure    Failing Keyword Teardown
    Log    This Should Be Executed

Run User keyword And Warn On Failure
    [Documentation]    PASS
    Run keyword And Warn On Failure    Exception In User Defined Keyword
    Log    This should be executed

Run Keyword And Warn On Failure With Syntax Error
    [Documentation]    FAIL    Assign mark '=' can be used only with the last variable.
    Run keyword And Continue On Failure    Syntax Error
    Fail    This Should Not Be Executed!

Run Keyword And Warn On Failure With Failure On Test Teardown
    [Documentation]    PASS
    [Teardown]    Run Keyword And Warn On Failure    Should Be Equal    x    y
    Log    This should Be Executed

Run Keyword And Warn On Failure With Timeout
    [Documentation]    FAIL    Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 seconds
    Run keyword And Warn On Failure    Sleep    1 second
    Fail    This Should Not Be Executed!

*** Keywords ***
Failing Keyword Teardown
    No Operation
    [Teardown]    Fail    Expected

Exception In User Defined Keyword
    Fail    Expected Warn In User Keyword

Syntax Error
    ${x} =    ${y} =    Create List    x    y
