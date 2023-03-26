*** Variables ***
${while limit}    ${0}

*** Test Cases ***
A single user keyword
    UK

Nested UK
    Nested UK    arg

Loops and stuff
    Loops and stuff

Recursion
    Recursion    ${3}

*** Keywords ***
UK
    [Tags]    robot:flatten
    Log    From the main kw
    RETURN    42

Nested UK
    [Arguments]    ${arg}
    [Tags]    robot:flatten
    Log    ${arg}
    Nest

Nest
    [Return]      foo
    Log    from nested kw

Loops and stuff
    [Tags]    robot:flatten
    FOR    ${i}    IN RANGE    5
        Log     inside for ${i}
        IF    ${i} > 3
            BREAK
        ELSE
            CONTINUE
        END
    END
    WHILE    ${while limit} < 5
        Log     inside while ${while limit}
        ${while limit}=   Set Variable   ${while limit + 1}
    END
    IF    True
        Log    inside if
    ELSE
        Fail
    END
    TRY
        Fail
    EXCEPT
        Log    inside except
    END

 Recursion
    [Arguments]    ${num}
    [Tags]    robot:flatten
    Log    Level: ${num}
    IF    ${num} < 10
        Recursion    ${num+1}
    END
