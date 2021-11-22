*** Test Cases ***
Try without END
    [Documentation]    FAIL    TRY has no closing END.
    TRY
        Fail   Error
    EXCEPT    Error

Try with argument
    [Documentation]    FAIL    TRY has an argument.
    TRY    I should not be here
        Fail   Error
    EXCEPT    Error
        No operation
    END
