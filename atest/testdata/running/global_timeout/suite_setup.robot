*** Settings ***
Suite Setup       Sleep    2s

*** Test Cases ***
Timeout In Suite Setup
    Log    Should not run
