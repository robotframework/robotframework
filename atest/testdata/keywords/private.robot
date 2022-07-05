*** Settings ***
Resource    private.resource
Resource    private2.resource
Resource    private3.resource

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

Local Private Keyword In Resource File Has Precedence Over Keywords In Another Resource
    Use Local Private Keyword Instead Keywords From Other Resources

Keyword With Same Name Should Resolve Public Keyword
    Same Name

If Both Keywords Are Private Raise Multiple Keywords Found
    [Documentation]    FAIL Multiple keywords with name 'Private Keyword In All Resources' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}private.Private Keyword In All Resources
    ...    ${SPACE*4}private2.Private Keyword In All Resources
    ...    ${SPACE*4}private3.Private Keyword In All Resources
    Private Keyword In All Resources

If One Keyword Is Public And Multiple Private Keywords Run Public And Warn
    Private In Two Resources And Public In One

*** Keywords ***
Public Keyword
    Private Keyword

Private Keyword
    [Tags]    robot:private
    No Operation
