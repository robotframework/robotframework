*** Settings ***
Documentation    Just a sample suite with a name took from the filename

*** Test Cases ***
Verify Suite Name
    Should Be Equal    ${SUITE_NAME}    Parent Init Suite.Another Suite