*** Test Cases ***
Flatten stuff
    [Tags]    test case tags should not match    flatten
    Keyword 2
    Keyword 3
    Keyword calling others
    Log    Flatten me too!!
    Keyword with tags not flatten
    Keyword with fags flatten

For loop
    FOR    ${i}    IN RANGE    10
        Log   index: ${i}
        Keyword 3
        Keyword 2
    END

Flatten IF in keyword
    Flatten IF in keyword

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

Keyword with tags not flatten
    [Documentation]    Doc of keyword not flatten
    [Tags]   hello    kitty
    Keyword 1

Keyword with fags flatten
    [Documentation]    Doc of flat tag
    [Tags]   hello    flatten
    Keyword 1

Flatten IF in keyword
    Log    Outside IF
    IF    True
        Log    Inside IF
    ELSE IF    True
        Fail    Not run
    ELSE
        Fail    Not run
    END
    IF    True
        IF    True
            Log    Nested IF
            Countdown
        END
    END

Countdown
    [Arguments]    ${count}=${3}
    IF    ${count} > 0
        Log    ${count}
        Countdown    ${count - 1}
    ELSE
        Log    BANG!
    END
