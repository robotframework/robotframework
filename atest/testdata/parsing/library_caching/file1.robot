*** Settings ***
Library           OperatingSystem
Resource          resource.robot

*** Test Cases ***
Test 1.1
    No Operation
    Directory Should Exist    ${CURDIR}

Test 1.2
    Resource KW
