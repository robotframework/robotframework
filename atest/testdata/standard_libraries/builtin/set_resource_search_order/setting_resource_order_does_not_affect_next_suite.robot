*** Settings ***
Resource          resource1.robot
Resource          resource2.robot

*** Test Cases ***
Default Resource Order Should Be Suite Specific
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Get Name' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}resource1.Get Name
    ...    ${SPACE*4}resource2.Get Name
    Get Name
