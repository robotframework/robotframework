*** Test Cases ***
Try without END
    [Documentation]    FAIL    TRY has no closing END.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed

Try without body
    [Documentation]    FAIL    TRY block cannot be empty.
    TRY
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

Try without except or finally
    [Documentation]    FAIL    TRY block must be followed by EXCEPT or FINALLY block"
    TRY
        Fail   Should not be executed
    END

Try with argument
    [Documentation]    FAIL    TRY has an argument.
    TRY    I should not be here
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

Except without body
    [Documentation]    FAIL    EXCEPT block cannot be empty.
    TRY
        Fail   Should not be executed
    EXCEPT    foo
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

Default except not last
    [Documentation]    FAIL    Default (empty) EXCEPT must be last.
    TRY
        Fail   Should not be executed
    EXCEPT
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

Multiple default excepts
    [Documentation]    FAIL    Multiple default (empty) EXCEPT blocks
    TRY
        Fail   Should not be executed
    EXCEPT
        Fail   Should not be executed
    EXCEPT
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

AS not the second last token
    [Documentation]    FAIL    AS must be second to last.
    TRY
        Fail   Should not be executed
    EXCEPT    AS    foo    ${foo}
        Fail   Should not be executed
    END

Invalid AS variable
    [Documentation]    FAIL    Invalid AS variable 'foo'.
    TRY
        Fail   Should not be executed
    EXCEPT    AS    foo
        Fail   Should not be executed
    END

Else with argument
    [Documentation]    FAIL    ELSE has condition.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    ELSE    I should not be here
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

Else without body
    [Documentation]    FAIL    ELSE block cannot be empty.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    ELSE
    FINALLY
        Fail   Should not be executed
    END

Multiple else blocks
    [Documentation]    FAIL    Multiple ELSE blocks.
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

Finally with argument
    [Documentation]    FAIL    FINALLY has an argument.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY    I should not be here
        Fail   Should not be executed
    END

Finally without body
    [Documentation]    FAIL    FINALLY block cannot be empty.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
    END

Multiple finally blocks
    [Documentation]    FAIL    Multiple FINALLY blocks.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    END

Else before except
    [Documentation]    FAIL    ELSE block before EXCEPT block.
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

Finally before except
    [Documentation]    FAIL    FINALLY block before EXCEPT block.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
            Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    EXCEPT    Error
        Fail   Should not be executed
    END

Finally before else
    [Documentation]    FAIL    FINALLY block before ELSE block.
    TRY
        Fail   Should not be executed
    EXCEPT    Error
            Fail   Should not be executed
    FINALLY
        Fail   Should not be executed
    ELSE
        Fail   Should not be executed
    END
