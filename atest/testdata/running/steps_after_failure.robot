*** Test Cases ***
Library keyword after failure
    [Documentation]    FAIL    This fails
    No operation
    Fail    This fails
    Fail    This should not be run
    Fail    This should not be run
    Fail    This should not be run
    Fail    This should not be run
    Fail    This should not be run
    [Teardown]    Log    This is run

User keyword after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    User keyword

Non-existing keyword after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    This does not exist

Invalid keyword usage after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    No Operation    with    too    many    args

Assignment after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    ${x} =    Not run
    ${x}      Not run
    ${x}    ${y} =    Not run
    ${x}    ${y}      Not run

IF after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    IF    True
        Fail    This should not be run
    ELSE
        ${x} =    Fail    This should not be run
    END

FOR after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    FOR    ${x}    IN    1    2    3
        Fail    This should not be run
        ${x}    Fail    This should not be run either
    END

TRY after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    TRY
        Fail    This should not be run
    EXCEPT    ${nonex}
        ${x}    Fail    This should not be run either
    ELSE
        Neither should ELSE
    FINALLY
        Nor FINALLY
    END

WHILE after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    WHILE    False
        Fail    This should not be run
        ${x}    Fail    This should not be run either
        Neither should this
    END
    WHILE    True
        Fail    This should not be run
        Neither should this
    END
    WHILE    whatever
        Fail    This should not be run
    END

RETURN after failure
    [Documentation]    FAIL    This fails
    ${result} =    RETURN after failure
    Fail    ${result}

BREAK and CONTINUE after failure
    [Documentation]    FAIL    This fails
    WHILE    True
        Fail    This fails
        CONTINUE
        BREAK
    END
    WHILE    whatever
        CONTINUE
        BREAK
    END

Nested control structure after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    FOR    ${x}    IN    1    2    3
        IF    True
            FOR    ${y}    IN RANGE    ${x}
                Fail    This should not be run
                Fail    This should not be run
                Fail    This should not be run
            END
            Fail    This should not be run
        ELSE
            WHILE    whatever
                Fail    This should not be run
                Neither should this
            END
            TRY
                Not run
            EXCEPT    Whatever
                BREAK
            END
        END
        Fail    This should not be run
    END
    Fail    This should not be run

Failure in user keyword
    [Documentation]    FAIL    This fails
    In user keyword
    Fail    This should not be run

Failure in IF branch
    [Documentation]    FAIL    This fails
    IF    True
        Fail    This fails
        Fail    This should not be run
    ELSE
        Fail    This should not be run
    END
    Fail    This should not be run

Failure in ELSE IF branch
    [Documentation]    FAIL    This fails
    IF    False
        Fail    This should not be run
    ELSE IF    True
        Fail    This fails
        Fail    This should not be run
    ELSE
        Fail    This should not be run
    END
    Fail    This should not be run

Failure in ELSE branch
    [Documentation]    FAIL    This fails
    IF    False
        Fail    This should not be run
    ELSE
        Fail    This fails
        Fail    This should not be run
    END
    Fail    This should not be run

Failure in FOR iteration
    [Documentation]    FAIL    This fails
    FOR    ${x}    IN RANGE    100
        Fail    This fails
        Fail    This should not be run
    END
    Fail    This should not be run

*** Keywords ***
User keyword
    Fail    This should not be run

In user keyword
    Fail    This fails
    Fail    This should not be run
    Fail    This should not be run

RETURN after failure
    Fail    This fails
    RETURN    ${not evaluated}
    Not executed
