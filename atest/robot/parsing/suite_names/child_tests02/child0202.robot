*** Settings ***
Documentation       Suite without custom name

Name                Child witout parent init


*** Test Cases ***
Verify That Suite Name is not a file like name
    Should Not Contain    ${SUITE_NAME}    Parent Init Suite.Child Tests02.Child0202

Verify Suite Name
    Should Contain    ${SUITE_NAME}    Parent Init Suite.Child Tests02.Child witout parent init
