*** Keywords ***
Private Keyword In Resource 2
    [Tags]    robot:private
    No Operation

Private Keyword In All Resources
    [Tags]    robot: private
    No Operation

Private In Two Resources And Public In One
    [Tags]    robot: private
    Log    private2.resource

Same Name
    [Tags]    robot:private
    No Operation
