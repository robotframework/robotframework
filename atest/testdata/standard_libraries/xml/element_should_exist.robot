*** Settings ***
Library           XML
Resource          xml_resource.robot

*** Test Cases ***
Get Element Count
    [Template]    Count Should Be
    nonex       0
    another     1
    .           1
    .//child    4

Element Should Exist Passes When There Are One Or More Matches
    Element Should Exist    ${TEST}    another/child
    Element Should Exist    ${TEST}    xpath=child

Element Should Exist Fails When There Are No Matches
    [Documentation]    FAIL    No element matching 'nönëx' found.
    Element Should Exist    <root/>    nönëx

Element Should Exist With Custom Error Message
    [Documentation]    FAIL    My error
    Element Should Exist    ${TEST}    xpath=another/child    message=Not used
    Element Should Exist    <root/>    nonex    My error

Element Should Not Exist Passes When There Are No Matches
    Element Should Not Exist    ${TEST}    nonex
    Element Should Not Exist    <root/>    xpath=child

Element Should Not Exist Fails When There Is One Match
    [Documentation]    FAIL    One element matching 'another/child' found.
    Element Should Not Exist    ${TEST}    xpath=another/child

Element Should Not Exist Fails When There Are Multiple Matches
    [Documentation]    FAIL    Multiple elements (4) matching './/child' found.
    Element Should Not Exist    ${TEST}    xpath=.//child

Element Should Not Exist With Custom Error Message
    [Documentation]    FAIL    My error
    Element Should Not Exist    <root/>    nonex    Not used
    Element Should Not Exist    ${TEST}    xpath=another/child    message=My error

*** Keywords ***
Count Should Be
    [Arguments]    ${xpath}    ${expected}
    ${count} =    Get Element Count    ${TEST}    xpath=${xpath}
    Should Be Equal As Integers    ${count}    ${expected}
