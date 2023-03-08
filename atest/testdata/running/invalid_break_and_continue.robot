*** Test cases ***
CONTINUE in test case
    [Documentation]    FAIL CONTINUE is not allowed in this context.
    Log    all good
    CONTINUE
    Fail    Should not be executed

CONTINUE in keyword
    [Documentation]    FAIL CONTINUE is not allowed in this context.
    Continue in keyword

CONTINUE in IF
    [Documentation]    FAIL CONTINUE can only be used inside a loop.
    IF    True
        Log    nice!
        CONTINUE
    END
    Fail    Should not be executed

CONTINUE in ELSE
    [Documentation]    FAIL CONTINUE can only be used inside a loop.
    IF    False
        Fail
    ELSE
        Log    nice!
        CONTINUE
    END
    Fail    Should not be executed

CONTINUE in TRY
    [Documentation]    FAIL CONTINUE can only be used inside a loop.
    TRY
        CONTINUE
    EXCEPT
        Fail
    END
    Fail    Should not be executed

CONTINUE in EXCEPT
    [Documentation]    FAIL CONTINUE can only be used inside a loop.
    TRY
        Fail
    EXCEPT
        CONTINUE
    END
    Fail    Should not be executed

CONTINUE in TRY-ELSE
    [Documentation]    FAIL CONTINUE can only be used inside a loop.
    TRY
        No operation
    EXCEPT
        Fail    Should not be executed
    ELSE
        CONTINUE
    END
    Fail    Should not be executed

CONTINUE with argument in FOR
    [Documentation]    FAIL CONTINUE does not accept arguments, got 'should not work'.
    FOR    ${i}    IN     1    2
        Log    ${i}
        CONTINUE    should not work
    END
    Fail    Should not be executed

CONTINUE with argument in WHILE
    [Documentation]    FAIL CONTINUE does not accept arguments, got 'should', 'not' and 'work'.
    WHILE    True
        No operation
        CONTINUE    should    not    work
    END
    Fail    Should not be executed

BREAK in test case
    [Documentation]    FAIL BREAK is not allowed in this context.
    Log    all good
    BREAK
    Fail    Should not be executed

BREAK in keyword
    [Documentation]    FAIL BREAK is not allowed in this context.
    Break in keyword

BREAK in IF
    [Documentation]    FAIL BREAK can only be used inside a loop.
    IF    True
        Log    nice!
        BREAK
    END
    Fail    Should not be executed

BREAK in ELSE
    [Documentation]    FAIL BREAK can only be used inside a loop.
    IF    False
        Fail
    ELSE
        Log    nice!
        BREAK
    END
    Fail    Should not be executed

BREAK in TRY
    [Documentation]    FAIL BREAK can only be used inside a loop.
    TRY
        BREAK
    EXCEPT
        Fail
    END
    Fail    Should not be executed

BREAK in EXCEPT
    [Documentation]    FAIL BREAK can only be used inside a loop.
    TRY
        Fail
    EXCEPT
        BREAK
    END
    Fail    Should not be executed

BREAK in TRY-ELSE
    [Documentation]    FAIL BREAK can only be used inside a loop.
    TRY
        No operation
    EXCEPT
        Fail    Should not be executed
    ELSE
        BREAK
    END
    Fail    Should not be executed

BREAK with argument in FOR
    [Documentation]    FAIL BREAK does not accept arguments, got 'should not work'.
    FOR    ${i}    IN     1    2
        Log    ${i}
        BREAK    should not work
    END
    Fail    Should not be executed

BREAK with argument in WHILE
    [Documentation]    FAIL BREAK does not accept arguments, got 'should', 'not' and 'work'.
    WHILE    True
        No operation
        BREAK    should    not    work
    END
    Fail    Should not be executed


*** Keywords ***
CONTINUE in keyword
    Log    all good
    CONTINUE
    Fail    Should not be executed

BREAK in keyword
    Log    all good
    BREAK
    Fail    Should not be executed
