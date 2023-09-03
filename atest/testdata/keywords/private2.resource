*** Keywords ***
Private Keyword In Resource 2
    [Tags]    robot:private
    No Operation

Private Keyword In All Resources
    [Tags]    robot: private
    Fail    Not executed

Private In Two Resources And Public In One
    [Tags]    robot: private
    Log    private2.resource

Private In One Resource And Public In Another
    Log    private2.resource

Private In One Resource And Public In Two
    Fail    Not executed
    
Private In Resource 1 And 3 And Public In Resource 2
    Log    private2.resource
