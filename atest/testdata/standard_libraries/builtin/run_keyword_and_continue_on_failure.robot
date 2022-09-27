*** Settings ***
Library    Exceptions

*** Test Cases ***
Run Keyword And Continue On Failure
    [Documentation]    FAIL    Several failures occurred:\n\n
    ...    1) Expected Failure\n\n
    ...    2) Expected Failure 2
    Run keyword And Continue On Failure    Fail    Expected Failure
    Run keyword And Continue On Failure    Fail    Expected Failure 2
    Log    This should be executed

Run Keyword And Continue On Failure In For Loop
    [Documentation]    FAIL    Several failures occurred:\n\n
    ...    1) 3 != 0\n\n
    ...    2) 3 != 1\n\n
    ...    3) 3 != 2\n\n
    ...    4) 3 != 4\n\n
    ...    5) Stop here!!
    FOR    ${i}    IN RANGE    0    5
        Run keyword And Continue On Failure    Should Be Equal    ${3}    ${i}
    END
    Fail    Stop here!!
    Fail    This isn't executed anymore

Run User keyword And Continue On Failure
    [Documentation]    FAIL    Expected Failure
    Run keyword And Continue On Failure    Exception In User Keyword
    Log    This should be executed

Run Keyword And Continue On Failure With For Loops
    [Documentation]    FAIL    Several failures occurred:\n\n
    ...    1) KW: a\n\n
    ...    2) UK: a\n\n
    ...    3) KW: b\n\n
    ...    4) UK: b
    FOR    ${x}    IN    a    b
        Run Keyword and Continue on Failure    Fail    KW: ${x}
        Run Keyword and Continue on Failure    Exception In User Keyword    UK: ${x}
    END

Nested Run Keyword And Continue On Failure
    [Documentation]    FAIL    Several failures occurred:\n\n
    ...    1) Continuable in UK\n\n
    ...    2) Second continuable in UK\n\n
    ...    3) Non-continuable in UK\n\n
    ...    4) The End
    Run Keyword And Continue On Failure    RKACOF in UK
    Fail    The End

Run Keyword And Continue On Failure with failure in keyoword teardown
    [Documentation]    FAIL    Several failures occurred:\n\n
    ...    1) Keyword teardown failed:\n
    ...    Expected error\n\n
    ...    2) The End
    Run Keyword And Continue On Failure    Keyword With Failing Teardown
    Fail    The End

Run Keyword And Continue On Failure With Syntax Error
    [Documentation]    FAIL    Assign mark '=' can be used only with the last variable.
    Run keyword And Continue On Failure    Syntax Error
    Fail    This Should Not Be Executed!

Run Keyword And Continue On Failure With Timeout
    [Documentation]    FAIL    Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 seconds
    Run keyword And Continue On Failure    Sleep    1 second
    Fail    This Should Not Be Executed!

Run Keyword And Continue On Failure With Nonexisting Variable
    [Documentation]    FAIL    Several failures occurred:\n\n
    ...    1) Variable '${nonexisting}' not found.\n\n
    ...    2) Normal failure after continuable failure
    Run keyword And Continue On Failure    Log    ${nonexisting}
    Fail    Normal failure after continuable failure

Run Keyword And Continue On Failure With Nonexisting Extended Variable
    [Documentation]    FAIL   GLOB: Several failures occurred:\n\n
    ...    1) Resolving variable '\${list.nonex}' failed: AttributeError:*\n\n
    ...    2) Normal failure after continuable failure
    ${list} =  Create list    1    2
    Run keyword And Continue On Failure    Log    ${list.nonex}
    Fail    Normal failure after continuable failure

Run Keyword And Continue On Failure With Fatal Error
    [Documentation]    FAIL    FatalCatastrophyException: BANG!
    Run keyword And Continue On Failure    Exit On Failure
    Fail    This Should Not Be Executed!

Run Keyword And Continue On Failure With Fatal Error 2
    [Documentation]    FAIL    Test execution stopped due to a fatal error.
    No Operation

*** Keywords ***
Exception In User Keyword
    [Arguments]    ${msg}=Expected Failure
    Fail    ${msg}

RKACOF in UK
    Run Keyword And Continue On Failure    Fail    Continuable in UK
    Run Keyword And Continue On Failure    RKACOF in UK 2
    Fail    Non-continuable in UK

RKACOF in UK 2
    Run Keyword And Continue On Failure    Fail    Second continuable in UK

Keyword With Failing Teardown
    No Operation
    [Teardown]    Fail    Expected error

Syntax Error
    ${x} =    ${y} =    Create List    x    y
