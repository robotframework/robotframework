*** Test Cases ***
For loop in test
    FOR    ${x}    IN    foo    bar
        Log    ${x}
    END

Missing END
    FOR    ${x}    IN    foo    bar
        Log    ${x}
        Keyword
    END

Nested loop
    FOR    ${x}    IN    x
        FOR    ${y}    IN    y
            FOR    ${z}    IN    z
                Log    ${x}${y}${z}
            END
        END
    END

*** Keywords ***
For loop in keyword
    FOR    ${x}    IN    foo    bar
        Log    ${x}
    END
