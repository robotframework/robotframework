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
    Use Local Private Keyword Instead Of Keywords From Other Resources

Search Order Has Precedence Over Local Private Keyword In Resource File
    [Setup]    Set Library Search Order    private2    private3
    Use Search Order Instead Of Private Keyword When Prioritized Resource Keyword Is Public
    [Teardown]    Set Library Search Order

Imported Public Keyword Has Precedence Over Imported Private Keywords
    Private In One Resource And Public In Another
    Use Imported Public Keyword Instead Instead Of Imported Private Keyword

If All Keywords Are Private Raise Multiple Keywords Found
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Private Keyword In All Resources' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}private.Private Keyword In All Resources
    ...    ${SPACE*4}private2.Private Keyword In All Resources
    ...    ${SPACE*4}private3.Private Keyword In All Resources
    Private Keyword In All Resources

If More Than Two Keywords Are Public Raise Multiple Keywords Found
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Private In One Resource And Public In Two' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}private2.Private In One Resource And Public In Two
    ...    ${SPACE*4}private3.Private In One Resource And Public In Two
    Private In One Resource And Public In Two

*** Keywords ***
Public Keyword
    Private Keyword

Private Keyword
    [Tags]    robot:private
    No Operation
