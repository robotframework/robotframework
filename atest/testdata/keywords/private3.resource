*** Keywords ***
Private In Two Resources And Public In One
    Log    private3.resource

Private Keyword In All Resources
    [Tags]    ROBOT: PRIVATE
    Fail    Not executed

Private In One Resource And Public In Another
    [Tags]    ROBOT: PRIVATE
    Fail    Not executed

Private In One Resource And Public In Two
    Fail    Not executed

Private In Resource 1 And 3 And Public In Resource 2
    [Tags]    ROBOT: PRIVATE
    Fail    Not executed
