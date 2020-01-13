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

Old for loop in test
    FOR    ${x}    IN    foo    bar
        Log    ${x}
    END
    FOR    ${x}    IN    quux    zap
        Log    ${x}
    END

*** Keywords ***
For loop in keyword
    FOR    ${x}    IN    foo    bar
        Log    ${x}
    END

Old for loop in keyword
    FOR    ${x}    IN    foo    bar
        Log    ${x}
    END
