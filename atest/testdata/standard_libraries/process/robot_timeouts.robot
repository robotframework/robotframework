*** Settings ***
Library           Process

*** Test Cases ***
Test timeout
    [Documentation]    FAIL    Test timeout 500 milliseconds exceeded.
    [Timeout]    0.5s
    Run Process    python    -c    import time; time.sleep(5)

Keyword timeout
    [Documentation]    FAIL    Keyword timeout 500 milliseconds exceeded.
    Keyword timeout

*** Keywords ***
Keyword timeout
    [Timeout]    0.5s
    Run Process    python    -c    import time; time.sleep(5)
