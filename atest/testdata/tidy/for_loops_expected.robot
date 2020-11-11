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

*** Keywords ***
For loop in keyword
    FOR    ${x}    IN    foo    bar
        Log    ${x}
    END
