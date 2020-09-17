*** Settings ***
Library    skiplib

*** Test Cases ***
Skip Keyword
    [Documentation]    SKIP
    Skip

Skip with Library Keyword
    [Documentation]    SKIP Show must not got on
    Skip with Message    Show must not got on

Skip Keyword with Custom Message
    [Documentation]    SKIP Skipped due to reasons
    Skip    Skipped due to reasons

Skipped in Setup
    [Documentation]    SKIP Skipped in setup:\nSetup skip
    [Setup]    Skip     Setup skip
    Pass
