*** Test Cases ***
For Loop In Test
    FOR    ${pet}    IN    cat    dog    horse
        Log    ${pet}
    END

For In Range Loop In Test
    FOR    ${i}    IN RANGE    10
        Log    ${i}
    END
