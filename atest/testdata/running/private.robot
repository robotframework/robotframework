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

*** Keywords ***
Public Keyword
    Private Keyword

Private Keyword
    [Tags]    robot:private
    Log    Hello
