*** Settings ***
Library           OperatingSystem

*** Keywords ***
Resource KW
    Directory Should Exist    ${CURDIR}
