*** Settings ***
Resource    private.resource

*** Test Cases ***
Valid Usage With Local Keyword
    Public Keyword

Invalid Usage With Local Keyword
    Private Keyword

Valid Usage With Resource Keyword
    Public Keyword In Resource

Invalid Usage With Resource Keyword
    Private Keyword In Resource

Invalid Usage In Resource file
    Call Private Keyword From Private 2 Resource

Keyword With Same Name Should Resolve Public Keyword
    Same Name

If Both Keywords Are Private Raise Multiple Keywords Found
    [Documentation]    FAIL Multiple keywords with name 'Nested Private Keyword' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}private.Nested Private Keyword
    ...    ${SPACE*4}private2.Nested Private Keyword
    First Public Keyword With Nested Private Keyword
    Second Public Keyword With Nested Private Keyword

*** Keywords ***
Public Keyword
    Private Keyword

Private Keyword
    [Tags]    robot:private
    Log    Hello
