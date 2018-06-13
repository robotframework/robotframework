*** Test Cases ***
Dictionary test
    [Tags]    collections
    ${dict} =    Create Dictionary    key    value
    Log    ${dict}

Test with a rather long name here we have and the name really is pretty long long long long longer than you think it could be
    [Tags]    this test also has a pretty long tag that really is long long long long long longer than you think it could be
    Keyword we have here is rather long long long long long longer than you think it could be be be be be be beeeeeee
    This keyword gets many arguments
    ...    it    really    gets    many    arguments
    ...    it    really    gets    many    arguments
    ...    it    really    gets    many    arguments
    ...    it    really    gets    many    arguments
    ...    it    really    gets    many    arguments
    ...    it    really    gets    many    arguments

*** Keywords ***
Keyword we have here is rather long long long long long longer than you think it could be be be be be be beeeeeee
    No Operation

This keyword gets many arguments
    [Arguments]    @{args}
    Log many    @{args}
