*** Test Cases ***
Try without END
    [Documentation]    FAIL    TRY has no closing END.
    TRY
        Fail   Error
    EXCEPT    Error

Try without except or finally
    [Documentation]    FAIL    TRY block must have EXCEPT or FINALLY block.
    TRY
        Log    1234
    END

Try with argument
    [Documentation]    FAIL    TRY has an argument.
    TRY    I should not be here
        Fail   Error
    EXCEPT    Error
        No operation
    END

Try else with argument
    [Documentation]    FAIL    ELSE has condition.
    TRY
        Fail   Error
    EXCEPT    Error
        No operation
    ELSE    I should not be here
        No operation
    END


Finally with argument
    [Documentation]    FAIL    FINALLY has an argument.
    TRY
        Fail   Error
    EXCEPT    Error
        No operation
    FINALLY    I should not be here
        No operation
    END
