*** Settings ***
Documentation    Just a sample suite with a name took from the filename

*** Test Cases ***
Verify That Suite Name is not a file like name
    Should Not Be Equal    ${SUITE_NAME}    Parent Init Suite.Child Tests01.Child0101

Verify Suite Name
    Should Be Equal    ${SUITE_NAME}    Parent Init Suite.Child Suite01 Name.Child0101