*** Settings ***
Resource    private2.resource

*** Keywords ***
Public Keyword In Resource
    Private Keyword In Resource

Private Keyword In Resource
    [Tags]    robot:private
    Log    Hello

Call Private Keyword From Private 2 Resource
    Private Keyword In Resource 2
