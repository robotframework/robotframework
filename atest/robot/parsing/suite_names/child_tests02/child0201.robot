*** Settings ***
Documentation       Just a sample suite with a name took from the filename


*** Test Cases ***
Verify suite name
    Should Contain    ${SUITE_NAME}    Parent Init Suite.Child Tests02.Child0201
