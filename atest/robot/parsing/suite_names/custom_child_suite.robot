*** Settings ***
Documentation       Just a sample suite with a name took from the filename

Name                Child Suite


*** Test Cases ***
Verify That Suite Name is not a file like name
    Should Not Contain    ${SUITE_NAME}    Parent Init Suite.Custom Shild Suite

Verify Suite Name
    Should Contain    ${SUITE_NAME}    Parent Init Suite.Child Suite
