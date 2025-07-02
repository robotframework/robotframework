*** Test Cases ***
Flatten stuff
    [Documentation]    FAIL    Expected e&<aped failure!
    [Tags]    test case tags should not match    flatten
    Keyword 2
    Keyword 3
    Keyword calling others
    Log    Flatten me too!!
    Keyword with tags not flatten
    Keyword with tags and no doc flatten
    Keyword with tags and message flatten

FOR loop
    FOR    ${i}    IN RANGE    10
        Log   index: ${i}
        Keyword 3
        Keyword 2
    END

WHILE loop
    ${i}=    Set variable    ${0}
    WHILE    $i < 10
        Log   index: ${i}
        Keyword 3
        Keyword 2
        ${i}=    Evaluate    $i + 1
    END

Flatten controls in keyword
    Flatten controls in keyword

*** Keywords ***
Keyword 3
    [Documentation]    Doc of keyword 3
    [Tags]    kw3
    [Timeout]    3 minutes
    Log    3
    Keyword 2

Keyword 2
    [Documentation]    Doc of keyword 2
    [Tags]    kw2
    [Timeout]    2m
    Log    2
    Keyword 1

Keyword 1
    [Arguments]    ${error}=
    [Documentation]    Doc of keyword 1
    IF    $error    Fail    ${error}
    Log    1

Keyword calling others
    Keyword 3
    Keyword 2
    Keyword 1

Keyword with tags not flatten
    [Documentation]    Doc of keyword not flatten
    [Tags]    hello    kitty
    Keyword 1

Keyword with tags and message flatten
    [Documentation]    Doc of flat keyword.
    [Tags]    hello    flatten
    Keyword 1    error=Expected e&<aped failure!

Keyword with tags and no doc flatten
    [Tags]    hi    flatten
    Keyword 1

Flatten controls in keyword
    Log    Outside IF
    IF    True
        Log    Inside IF
        Keyword 1
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
    FOR    ${i}    IN RANGE    3
        Log   FOR: ${i}
        Keyword 1
        CONTINUE
        Fail    Not run
    END
    WHILE    $i > 0
        Log   WHILE: ${i}
        Keyword 1
        ${i}=    Evaluate    $i - 1
        IF    $i >= 1    CONTINUE
        BREAK
    END
    TRY
        Fail
    EXCEPT
        Keyword 1
    FINALLY
        Log    finally
    END
    GROUP
        Log    Inside GROUP
    END
    VAR    ${x}    Using VAR
    RETURN    return value

Countdown
    [Arguments]    ${count}=${3}
    IF    ${count} > 0
        Log    ${count}
        Countdown    ${count - 1}
    ELSE
        Log    BANG!
    END
