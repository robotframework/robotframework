*** Settings ***
Library           libraryscope.Global
Library           libraryscope.Suite
Library           libraryscope.Test
Library           libraryscope.InvalidValue
Library           libraryscope.InvalidEmpty
Library           libraryscope.InvalidMethod
Library           libraryscope.InvalidNone

*** Keywords ***
Register All
    [Arguments]    ${name}
    libraryscope.Global.Register    ${name}
    libraryscope.Suite.Register    ${name}
    libraryscope.Test.Register    ${name}
    libraryscope.InvalidValue.Register    ${name}
    libraryscope.InvalidEmpty.Register    ${name}
    libraryscope.InvalidMethod.Register    ${name}
    libraryscope.InvalidNone.Register    ${name}

Invalids Should Have Registered
    [Arguments]    @{expected}
    libraryscope.InvalidValue.Should Be Registered    @{expected}
    libraryscope.InvalidEmpty.Should Be Registered    @{expected}
    libraryscope.InvalidMethod.Should Be Registered    @{expected}
    libraryscope.InvalidNone.Should Be Registered    @{expected}
