*** Settings ***
Suite Setup     Run Tests  ${EMPTY}    running/skip/
Resource        atest_resource.robot

*** Test Cases ***
Skip Keyword
    Check Test Case     Skip Keyword

Skip Keyword with Custom Message
    Check Test Case     Skip Keyword with Custom Message

Skipped in Setup
    Check Test Case    Skipped in Setup

Skip in Suite Setup
    Check Test Case    Skipped due to Suite Setup    status=SKIP
