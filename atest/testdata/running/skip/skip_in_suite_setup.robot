*** Settings ***
Suite Setup    Skip    Cannot go on

*** Test Cases ***
Skipped Due To Suite Setup
    [Documentation]    SKIP Skipped in parent suite setup:\nCannot go on
    Pass
