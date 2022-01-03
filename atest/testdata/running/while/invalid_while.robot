*** Test Cases ***
While without END
    [Documentation]    FAIL WHILE loop has no closing END.
    WHILE    True
        Log    a recursion!

While without condition
    [Documentation]    FAIL WHILE has no condition.
    WHILE
        Log    a recursion!
    END

While with multiple conditions
    [Documentation]    FAIL WHILE has no condition.
    WHILE
        Log    a recursion!
    END

While without body
    [Documentation]    FAIL WHILE loop has empty body.
    WHILE    True
    END
