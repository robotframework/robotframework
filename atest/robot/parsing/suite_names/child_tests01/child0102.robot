*** Settings ***
Documentation       Suite without custom name but with custom name in init

Name          Child 0102 Suite


*** Test Cases ***
Verify That Suite Name is not a file like name
    Should Not Contain    ${SUITE_NAME}    Parent Init Suite.Child Tests01.Child0101
    Should Not Contain    ${SUITE_NAME}    Parent Init Suite.Child Suite01 Name.Child0101

Verify Suite Name
    Should Contain    ${SUITE_NAME}    Parent Init Suite.Child Suite01 Name.Child 0102 Suite
