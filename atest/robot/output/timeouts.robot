*** Settings ***
Suite Setup    Run Tests  ${EMPTY}  misc/timeouts.robot
Resource  atest_resource.robot
Test Template    Element Should Have Timeout

*** Test Cases ***
Test timeout is written to XML
    1 minute 42 seconds

Keyword timeout is written to XML
    42 seconds   xpath=kw

Empty keyword timeout should not be written to XML
    ${None}  xpath=kw/kw

Empty test timeout should not be written to XML
    ${None}  index=-1

*** Keywords ***
Element Should Have Timeout   [Arguments]   ${value}    ${xpath}=.   ${index}=0
    @{tests}=   Get Elements    ${OUTFILE}   */test
    Element Attribute Should Be   @{tests}[${index}]  timeout   ${value}   ${xpath}
