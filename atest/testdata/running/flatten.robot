*** Variables ***
${LIMIT}         ${0}

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
    Log    from nested kw
    RETURN      foo
    Log    not logged

Loops and stuff
    [Tags]    robot:flatten
    FOR    ${i}    IN RANGE    5
        Log     inside for ${i}
        IF    ${i} > 1
            BREAK
        ELSE
            CONTINUE
        END
    END
    WHILE    ${LIMIT} < 3
        Log     inside while ${LIMIT}
        VAR    ${LIMIT}    ${LIMIT + 1}
    END
    TRY
        IF    True
            Log    inside if
        ELSE
            Fail    not run
        END
        Fail    fail inside try
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
