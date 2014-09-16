*** Test Cases ***
Flatten stuff
    Keyword 2
    Keyword 3
    Keyword calling others
    Log    Flatten me too!!

For loop
    :FOR    ${i}    IN RANGE    10
    \    Log   index: ${i}
    \    Keyword 3
    \    Keyword 2

*** Keywords ***
Keyword 3
    [Documentation]    Doc of keyword 3
    Log    3
    Keyword 2

Keyword 2
    [Documentation]    Doc of keyword 2
    Log    2
    Keyword 1

Keyword 1
    [Documentation]    Doc of keyword 1
    Log    1

Keyword calling others
    Keyword 3
    Keyword 2
    Keyword 1
