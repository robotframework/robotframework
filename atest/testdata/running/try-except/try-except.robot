*** Test Cases ***
Try with no failures
    TRY
        No operation
    EXCEPT    failure
        Fail    Should not be executed

Try with first except executed
    TRY
        Fail    failure
    EXCEPT    failure
        No operation
