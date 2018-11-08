*** Settings ***
Library           timeouts_with_logging.py
Test Timeout      ${TIMEOUT}

*** Variables ***
${TIMEOUT}        25 milliseconds

*** Test Cases ***
RF logger 1
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    RF logger

RF logger 2
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    RF logger

RF logger 3
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    RF logger

RF logger 4
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    RF logger

RF logger 5
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    RF logger

Python logging 1
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    Python logging

Python logging 2
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    Python logging

Python logging 3
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    Python logging

Python logging 4
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    Python logging

Python logging 5
    [Documentation]    FAIL Test timeout ${TIMEOUT} exceeded.
    Python logging
