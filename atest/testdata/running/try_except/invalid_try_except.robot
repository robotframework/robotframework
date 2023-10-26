*** Test Cases ***
TRY without END
    [Documentation]    FAIL    TRY must have closing END.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed

TRY without body
    [Documentation]    FAIL    TRY branch cannot be empty.
    TRY
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

TRY without EXCEPT or FINALLY
    [Documentation]    FAIL    TRY structure must have EXCEPT or FINALLY branch.
    TRY
        Fail   Should not be executed
    END

TRY with ELSE without EXCEPT or FINALLY
    [Documentation]    FAIL    TRY structure must have EXCEPT or FINALLY branch.
    TRY
        Fail   Should not be executed
    ELSE
        Not run either
    END

TRY with argument
    [Documentation]    FAIL    TRY does not accept arguments, got 'I should not be here'.
    TRY    I should not be here
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

EXCEPT without body
    [Documentation]    FAIL    EXCEPT branch cannot be empty.
    TRY
        Fail   Should not be executed
    EXCEPT    foo
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

Default EXCEPT not last
    [Documentation]    FAIL    EXCEPT without patterns must be last.
    TRY
        Fail   Should not be executed
    EXCEPT
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

Multiple default EXCEPTs
    [Documentation]    FAIL    Only one EXCEPT without patterns allowed.
    TRY
        Fail   Should not be executed
    EXCEPT
        Fail   Should not be executed
    EXCEPT
        Fail   Should not be executed
    ELSE
        Fail   Should not be executed
    END

AS requires variable
    [Documentation]    FAIL    EXCEPT AS requires a value.
    TRY
        Fail   Should not be executed
    EXCEPT    AS
        Fail   Should not be executed
    END

AS accepts only one variable
    [Documentation]    FAIL    EXCEPT AS accepts only one value.
    TRY
        Fail   Should not be executed
    EXCEPT    AS    foo    ${foo}
        Fail   Should not be executed
    END

Invalid AS variable
    [Documentation]    FAIL    EXCEPT AS variable 'foo' is invalid.
    TRY
        Fail   Should not be executed
    EXCEPT    AS    foo
        Fail   Should not be executed
    END

ELSE with argument
    [Documentation]    FAIL    ELSE does not accept arguments, got 'I should not be here'.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    ELSE    I should not be here
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

ELSE without body
    [Documentation]    FAIL    ELSE branch cannot be empty.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    ELSE
    FINALLY
        Fail   Should not be executed
    END

Multiple ELSE blocks
    [Documentation]    FAIL    Only one ELSE allowed.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    ELSE
        Fail   Should not be executed
    ELSE
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

FINALLY with argument
    [Documentation]    FAIL    FINALLY does not accept arguments, got 'ooops', 'i', 'did', 'it' and 'again'.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY    ooops    i    did    it    again
        Fail   Should not be executed
    END

FINALLY without body
    [Documentation]    FAIL    FINALLY branch cannot be empty.
    TRY
        Fail   Should not be executed
    FINALLY
    END

Multiple FINALLY blocks
    [Documentation]    FAIL    Only one FINALLY allowed.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

ELSE before EXCEPT
    [Documentation]    FAIL    EXCEPT not allowed after ELSE.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
            Fail   Should not be executed
    ELSE
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

FINALLY before EXCEPT
    [Documentation]    FAIL    EXCEPT not allowed after FINALLY.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    END

FINALLY before ELSE
    [Documentation]    FAIL    ELSE not allowed after FINALLY.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    ELSE
        Fail   Should not be executed
    END

Template with TRY
    [Documentation]    FAIL    Templates cannot be used with TRY.
    [Template]    Log many
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    END

Template with TRY inside IF
    [Documentation]    FAIL    Templates cannot be used with TRY.
    [Template]    Log many
    IF    True
        TRY
            Fail   Should not be executed
        EXCEPT    Error
            Fail   Should not be executed
        END
    END

Template with IF inside TRY
    [Documentation]    FAIL
    ...    Multiple errors:
    ...    - TRY must have closing END.
    ...    - Templates cannot be used with TRY.
    [Template]    Log many
    TRY
        IF    True
            Fail    Should not be executed
        END
    FINALLY
        No Operation

BREAK in FINALLY
    [Documentation]    FAIL    BREAK cannot be used in FINALLY branch.
    WHILE    True
        TRY
            No Operation
        FINALLY
            BREAK
        END
    END

CONTINUE in FINALLY
    [Documentation]    FAIL    CONTINUE cannot be used in FINALLY branch.
    FOR    ${i}    IN    some    values
        TRY
            No Operation
        FINALLY
            CONTINUE
        END
    END

RETURN in FINALLY
    [Documentation]    FAIL    RETURN cannot be used in FINALLY branch.
    RETURN in FINALLY

Invalid TRY/EXCEPT causes syntax error that cannot be caught
    [Documentation]    FAIL    TRY branch cannot be empty.
    TRY
        TRY
        EXCEPT
            Fail    Not run
        END
    EXCEPT
        Fail    Not run because error cannot be caught
    ELSE
        Fail    Not run either
    END

Dangling FINALLY
    [Documentation]    FAIL FINALLY is not allowed in this context.
    IF    ${True}
        FINALLY
    END

*** Keywords ***
RETURN in FINALLY
    TRY
        No Operation
    FINALLY
        RETURN
    END
