*** Settings ***
Resource    private2.resource

*** Keywords ***
Public Keyword In Resource
    Private Keyword In Resource

Private Keyword In Resource
    [Tags]    robot:private
    No Operation

Call Private Keyword From Private 2 Resource
    Private Keyword In Resource 2

Same Name
    No Operation

First Public Keyword With Nested Private Keyword
    Nested Private Keyword

Nested Private Keyword
    [Tags]    robot:private
    No Operation

Possible Keyword
    No Operation
