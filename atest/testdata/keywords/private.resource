*** Settings ***
Resource    private2.resource

*** Keywords ***
Public Keyword In Resource
    Private Keyword In Resource

Private Keyword In Resource
    [Tags]    robot:private
    No Operation

Use Local Private Keyword Instead Keywords From Other Resources
    Private Keyword In All Resources
    Private In Two Resources And Public In One

Private Keyword In All Resources
    [Tags]    ROBOT: private
    Log    private.resource

Private In Two Resources And Public In One
    [Tags]    RoBoT:PrIvAtE
    Log    private.resource

Call Private Keyword From Private 2 Resource
    Private Keyword In Resource 2

Same Name
    No Operation
