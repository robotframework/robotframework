*** Keywords ***
Short Timeout Keyword
    [Timeout]    0.5s
    Sleep    10s

Long Timeout Keyword
    [Timeout]    10s
    Sleep    10s

*** Test Cases ***
Global Timeout Wins Over Longer Test Timeout
    [Documentation]    FAIL Total Execution timeout 1 second exceeded.
    [Timeout]    5s
    Sleep    10s

Shorter Test Timeout Wins Over Global Timeout
    [Documentation]    FAIL Test timeout 500 milliseconds exceeded.
    [Timeout]    0.5s
    Sleep    10s

Shorter Keyword Timeout Wins Over Global Timeout
    [Documentation]    FAIL Keyword timeout 500 milliseconds exceeded.
    Short Timeout Keyword

Global Timeout Wins Over Longer Keyword Timeout
    [Documentation]    FAIL Total Execution timeout 1 second exceeded.
    Long Timeout Keyword
