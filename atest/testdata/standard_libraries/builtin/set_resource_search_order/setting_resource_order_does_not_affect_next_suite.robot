*** Settings ***
Resource        resource1.robot
Resource        resource2.robot

*** Test Cases ***
Default Resource Order Should Be Suite Specific
    [Documentation]  FAIL Multiple keywords with name 'Get Name' found.\n Give the full name of the keyword you want to use.\n Found: 'resource1.Get Name' and 'resource2.Get Name'
    Get Name

