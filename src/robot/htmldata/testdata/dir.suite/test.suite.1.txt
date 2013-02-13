*** settings ***
Library   Collections
Suite Setup    User Keyword

*** test cases ***
list test
    ${list}=  Create List  foo  bar  quux
    Log  ${list}
    [Tags]   collections

*** Keywords ***
User Keyword
    User Keyword 2
    No Operation
    ${ret} =    User Keyword 3

User Keyword 2
    Log    Several levels...
    User Keyword 3

User Keyword 3
    Log    <b>The End</b>    HTML
