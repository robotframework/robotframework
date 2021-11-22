*** Test Cases ***
Run Keyword With Maximum Time Failing On Library Keyword
    [Documentation]    FAIL
    ...    Keyword timeout 1 second exceeded.
    Run Keyword With Maximum Time  1 second  Sleep  2 seconds

Run Keyword With Maximum Time Passing On Library Keyword
    Run Keyword With Maximum Time  2 seconds  Sleep  1 second

Run Keyword With Maximum Time Failing On User Defined Keyword
    [Documentation]    FAIL
    ...    Keyword timeout 1 second exceeded.
    Run Keyword With Maximum Time  1 second  Long Executing Keyword

Run Keyword With Maximum Time Passing On User Defined Keyword
    Run Keyword With Maximum Time  3 seconds  Long Executing Keyword

Run Keyword With Maximum Time With Failing On Customizable Timeout Keyword
    [Documentation]    FAIL
    ...    Keyword timeout 500 milliseconds exceeded.
    Run Keyword With Maximum Time  1 second  Keyword With Customizable Timeout  0.5 seconds

Run Keyword With Maximum Time With Passing On Customizable Timeout Keyword
    Run Keyword With Maximum Time  3 seconds  Keyword With Customizable Timeout  2.5 seconds

Run Keyword With Maximum Time Failing in Setup
    [Documentation]    FAIL
    ...    Setup failed:
    ...    Keyword timeout 1 second exceeded.
    [Setup]  Run Keyword With Maximum Time  1 second  Long Executing Keyword
    No Operation

Run Keyword With Maximum Time Passing in Setup
    [Setup]  Run Keyword With Maximum Time  3 second  Long Executing Keyword
    No Operation

Run Keyword With Maximum Time Failing in Teardown
    [Documentation]    FAIL
    ...    Keyword teardown failed:
    ...    Keyword timeout 1 second exceeded.
    Keyword With Teardown Fail

Run Keyword With Maximum Time Passing in Teardown
    Keyword With Teardown Pass

*** Keywords ***
Long Executing Keyword
    Sleep  2

Keyword With Customizable Timeout
    [Arguments]    ${timeout}
    [Timeout]    ${timeout}
    Sleep  2

Keyword With Teardown Fail
    No Operation
    [Teardown]  Run Keyword With Maximum Time  1 second  Long Executing Keyword

Keyword With Teardown Pass
    No Operation
    [Teardown]  Run Keyword With Maximum Time  3 second  Long Executing Keyword
