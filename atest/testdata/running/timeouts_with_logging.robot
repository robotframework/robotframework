*** Settings ***
Documentation     These tests validate the fix for
...               https://github.com/robotframework/robotframework/issues/2839
...
...               There used to be more tests here on the test data side, but
...               that started to cause weird problems on CI. Having these
...               four tests ought to be enough to prevent the original issue
...               from reappearing.
Library           timeouts_with_logging.py

*** Variables ***
${TIMEOUT}        25 milliseconds

*** Test Cases ***
Test timeout when logging using RF logger
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    [Timeout]    ${TIMEOUT}
    RF logger

Keyword timeout when logging using RF logger
    [Documentation]    FAIL Keyword timeout ${TIMEOUT} exceeded.
    Keyword timeout when logging with RF logger

Test timeout when logging using Python logger
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    [Timeout]    ${TIMEOUT}
    Python logger

Keyword timeout when logging using Python logger
    [Documentation]    FAIL Keyword timeout ${TIMEOUT} exceeded.
    Keyword timeout when logging with Python logger

*** Keywords ***
Keyword timeout when logging with RF logger
    [Timeout]    ${TIMEOUT}
    RF logger

Keyword timeout when logging with Python logger
    [Timeout]    ${TIMEOUT}
    Python logger
