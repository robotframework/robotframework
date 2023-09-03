*** Settings ***
Resource    private2.resource
Resource    private3.resource

*** Keywords ***
Public Keyword In Resource
    Private Keyword In Resource

Private Keyword In Resource
    [Tags]    robot:private
    No Operation

Use Local Private Keyword Instead Of Keywords From Other Resources
    Private Keyword In All Resources
    Private In Two Resources And Public In One

Use Search Order Instead Of Private Keyword When Prioritized Resource Keyword Is Public
    Private In Resource 1 And 3 And Public In Resource 2

Private Keyword In All Resources
    [Tags]    ROBOT: private
    Log    private.resource

Private In Two Resources And Public In One
    [Tags]    RoBoT:PrIvAtE
    Log    private.resource

Use Imported Public Keyword Instead Instead Of Imported Private Keyword
    Private In One Resource And Public In Another

Call Private Keyword From Private 2 Resource
    Private Keyword In Resource 2

Private In One Resource And Public In Two
    [Tags]    robot:private
    Fail    Not executed

Private In Local And One Resource And Public In Another
    [Tags]    robot:private
    Fail    Not executed
