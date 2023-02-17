*** Settings ***
Documentation       Suite without custom name but with custom name in init

Suite Name          Child 0102 Suite


*** Test Cases ***
Verify That Suite Name is not a file like name
    Should Not Be Equal    ${SUITE_NAME}    Robot.Parsing.Parent Init Suite.Child Tests01.Child0101
    Should Not Be Equal    ${SUITE_NAME}    Robot.Parsing.Parent Init Suite.Child Suite01 Name.Child0101

Verify Suite Name
    Should Be Equal    ${SUITE_NAME}    Robot.Parsing.Parent Init Suite.Child Suite01 Name.Child 0102 Suite
