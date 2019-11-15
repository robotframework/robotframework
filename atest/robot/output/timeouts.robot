*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    misc/timeouts.robot
Resource          atest_resource.robot

*** Test Cases ***
Test timeout is written to XML
    Element Should Have Timeout    1 minute 42 seconds

Keyword timeout is written to XML
    Element Should Have Timeout    42 seconds    element=kw

Empty test timeout should not be written to XML
    Element Should Not Have Timeout    index=-1

Empty keyword timeout should not be written to XML
    Element Should Not Have Timeout    element=kw/kw

*** Keywords ***
Element Should Have Timeout
    [Arguments]    ${value}    ${element}=.
    @{tests}=    Get Elements    ${OUTFILE}    */test
    Element Attribute Should Be    ${tests}[0]    value    ${value}    ${element}/timeout

Element Should Not Have Timeout
    [Arguments]    ${index}=0    ${element}=.
    @{tests}=    Get Elements    ${OUTFILE}    */test
    Element Should Not Exist    ${tests}[${index}]    ${element}/timeout
