*** Settings ***
Library           OperatingSystem
Resource          resource.robot

*** Test Cases ***
Test 2.1
    No Operation
    Directory Should Exist    ${CURDIR}

Test 2.2
    Resource KW
