*** Test Cases ***
FOR loop in test
    FOR    ${pet}    IN    cat    dog    horse
        Log    ${pet}
    END

FOR IN RANGE loop in test
    FOR    ${i}    IN RANGE    10
        Log    ${i}
    END
