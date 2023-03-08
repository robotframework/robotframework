*** Settings ***
Documentation       Just a sample suite with a name took from the filename


*** Test Cases ***
Verify suite name
    Should Be Equal    ${SUITE_NAME}    Robot.Parsing.Parent Init Suite.Child Tests02.Child0201
