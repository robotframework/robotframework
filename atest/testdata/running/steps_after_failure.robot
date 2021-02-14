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

IF after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    IF    True
        Fail    This should not be run
    ELSE
        Fail    This should not be run
    END

FOR after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    FOR    ${x}    IN    1    2    3
        Fail    This should not be run
        Fail    This should not be run either
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
            Fail    This should not be run
        END
        Fail    This should not be run
    END
    Fail    This should not be run

Non-existing keyword after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    This does not exist

Invalid keyword usage after failure
    [Documentation]    FAIL    This fails
    Fail    This fails
    No Operation    with    too    many    args

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
