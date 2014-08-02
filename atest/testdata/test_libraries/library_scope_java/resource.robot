*** Setting ***
Library           javalibraryscope.Global
Library           javalibraryscope.Suite
Library           javalibraryscope.Test
Library           javalibraryscope.InvalidValue
Library           javalibraryscope.InvalidEmpty
Library           javalibraryscope.InvalidMethod
Library           javalibraryscope.InvalidNull
Library           javalibraryscope.InvalidPrivate
Library           javalibraryscope.InvalidProtected

*** Keyword ***
Register All
    [Arguments]    ${name}
    javalibraryscope.Global.Register    ${name}
    javalibraryscope.Suite.Register    ${name}
    javalibraryscope.Test.Register    ${name}
    javalibraryscope.InvalidValue.Register    ${name}
    javalibraryscope.InvalidEmpty.Register    ${name}
    javalibraryscope.InvalidMethod.Register    ${name}
    javalibraryscope.InvalidNull.Register    ${name}
    javalibraryscope.InvalidPrivate.Register    ${name}
    javalibraryscope.InvalidProtected.Register    ${name}

Invalids Should Have Registered
    [Arguments]    @{expected}
    javalibraryscope.InvalidValue.Should Be Registered    @{expected}
    javalibraryscope.InvalidEmpty.Should Be Registered    @{expected}
    javalibraryscope.InvalidMethod.Should Be Registered    @{expected}
    javalibraryscope.InvalidNull.Should Be Registered    @{expected}
    javalibraryscope.InvalidPrivate.Should Be Registered    @{expected}
    javalibraryscope.InvalidProtected.Should Be Registered    @{expected}
