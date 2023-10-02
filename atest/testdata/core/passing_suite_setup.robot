*** Settings ***
Suite Setup       Set Suite Variable    $SETUP    Suite Setup Executed

*** Test Cases ***
Verify Suite Setup
    Should Be Equal    ${SETUP}    Suite Setup Executed
