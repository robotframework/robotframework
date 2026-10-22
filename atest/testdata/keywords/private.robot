*** Settings ***
Suite Setup       Private Keyword In Suite File
Suite Teardown    Private Keyword In Resource
Resource          private.resource
Resource          private2.resource
Resource          private3.resource

*** Test Cases ***
Test can call local public keyword
    Public Keyword In Suite File

Test can call local private keyword
    Private Keyword In Suite File

Test can call public resource keyword
    Public Keyword In Resource

Test calling private resource keyword causes warning
    Private Keyword In Resource

Resource keyword calling private keyword in another resource causes warning
    Call Private Keyword From Private 2 Resource

Resource keyword calling private keyword in suite file causes warning
    Call Private Keyword From Suite File

Local private keyword in resource has precedence over keywords in another resource
    Use Local Private Keyword Instead Of Keywords From Other Resources

Search order has precedence over local private keyword in resource
    [Setup]    Set Library Search Order    private2    private3
    Use Search Order Instead Of Private Keyword When Prioritized Resource Keyword Is Public
    [Teardown]    Set Library Search Order

Imported public keyword has precedence over imported private keyword
    Private In One Resource And Public In Another
    Use Imported Public Keyword Instead Instead Of Imported Private Keyword

Raise multiple keywords error if all keywords are private
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Private Keyword In All Resources' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}private.Private Keyword In All Resources
    ...    ${SPACE*4}private2.Private Keyword In All Resources
    ...    ${SPACE*4}private3.Private Keyword In All Resources
    Private Keyword In All Resources

Raise multiple keywords error if more than one keyword is public
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Private In One Resource And Public In Two' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}private2.Private In One Resource And Public In Two
    ...    ${SPACE*4}private3.Private In One Resource And Public In Two
    Private In One Resource And Public In Two

Test can call local private keyword with embedded arguments
    Private Keyword With An Argument

Resource keyword calling private keyword with embedded arguments in suite file causes warning
    Call Private Embedded Keyword From Suite File

*** Keywords ***
Public Keyword In Suite File
    Private Keyword In Suite File

Private Keyword In Suite File
    [Tags]    robot:private
    No Operation

Private Keyword With ${argument}
    [Tags]    robot:private
    Should Be Equal    ${argument}    An Argument
