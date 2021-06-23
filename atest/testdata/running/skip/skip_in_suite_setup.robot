*** Settings ***
Suite Setup    Skip    Cannot go on

*** Test Cases ***
Skip In Suite Setup
    [Documentation]    SKIP Skipped in parent suite setup:\nCannot go on
    Fail    Should not be executed!
