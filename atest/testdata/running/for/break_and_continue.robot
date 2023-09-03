*** Test Cases ***
With CONTINUE
    FOR    ${i}    IN     2     3     4
        CONTINUE
        Fail    should not be executed
    END

With CONTINUE inside IF
    [Documentation]    FAIL Oh no, got 4
    FOR    ${i}     IN RANGE    6
        IF    $i == 4
            Fail    Oh no, got 4
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

With CONTINUE inside TRY
    FOR    ${i}     IN RANGE    6
        TRY
            CONTINUE
            Fail    should not be executed
        EXCEPT
            Fail    should not be executed
        ELSE
            Log     all is fine!
        END
    END

With CONTINUE inside EXCEPT and TRY-ELSE
    FOR    ${i}     IN RANGE    6
        TRY
            Should not be equal    ${variable}    ${4}
        EXCEPT
            CONTINUE
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

With BREAK
    FOR    ${i}     IN RANGE    1000
        BREAK
        Fail    should not be executed
    END
    Should be equal    ${i}    ${0}

With BREAK inside IF
    FOR    ${i}     IN RANGE    6
        IF    $i == 3
            BREAK
            Fail    should not be executed
        END
    END

With BREAK inside TRY
    FOR    ${i}     IN RANGE    6
        TRY
            BREAK
            Fail    should not be executed
        EXCEPT
            Fail    should not be executed
        ELSE
            Fail    should not be executed
        END
        Fail    should not be executed
    Should be equal    ${i}    ${0}
    END

With BREAK inside EXCEPT
    FOR    ${i}     IN RANGE    6
        TRY
            Fail    This is excepted!
        EXCEPT    This is excepted!
            BREAK
        ELSE
            Fail    should not be executed
        END
        Fail    should not be executed
    END
    Should be equal    ${i}    ${0}

With BREAK inside TRY-ELSE
    FOR    ${i}     IN RANGE    6
        TRY
            No operation
        EXCEPT    This is excepted!
            Fail    This is excepted!
        ELSE
            BREAK
        END
        Fail    should not be executed
    END
    Should be equal    ${i}    ${0}

With CONTINUE in UK
    With CONTINUE in UK

With CONTINUE inside IF in UK
    [Documentation]    FAIL Oh no, got 4
    With CONTINUE inside IF in UK

With CONTINUE inside TRY in UK
    With CONTINUE inside TRY in UK

With CONTINUE inside EXCEPT and TRY-ELSE in UK
    With CONTINUE inside EXCEPT and TRY-ELSE in UK

With BREAK in UK
    With BREAK in UK

With BREAK inside IF in UK
    With BREAK inside IF in UK

With BREAK inside TRY in UK
    With BREAK inside TRY in UK

With BREAK inside EXCEPT in UK
    With BREAK inside EXCEPT in UK

With BREAK inside TRY-ELSE in UK
    With BREAK inside TRY-ELSE in UK

*** Keywords ***
With CONTINUE in UK
    FOR    ${i}    IN     2     3     4
        CONTINUE
        Fail    should not be executed
    END

With CONTINUE inside IF in UK
    [Documentation]    FAIL Oh no, got 4
    FOR    ${i}     IN RANGE    6
        IF    $i == 4
            Fail    Oh no, got 4
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

With CONTINUE inside TRY in UK
    FOR    ${i}     IN RANGE    6
        TRY
            CONTINUE
            Fail    should not be executed
        EXCEPT
            Fail    should not be executed
        ELSE
            Log     all is fine!
        END
    END

With CONTINUE inside EXCEPT and TRY-ELSE in UK
    FOR    ${i}     IN RANGE    6
        TRY
            Should not be equal    ${variable}    ${4}
        EXCEPT
            CONTINUE
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

With BREAK in UK
    FOR    ${i}     IN RANGE    1000
        BREAK
        Fail    should not be executed
    END
    Should be equal    ${i}    ${0}

With BREAK inside IF in UK
    FOR    ${i}     IN RANGE    6
        IF    $i == 3
            BREAK
            Fail    should not be executed
        END
    END

With BREAK inside TRY in UK
    FOR    ${i}     IN RANGE    6
        TRY
            BREAK
            Fail    should not be executed
        EXCEPT
            Fail    should not be executed
        ELSE
            Fail    should not be executed
        END
        Fail    should not be executed
    Should be equal    ${i}    ${0}
    END

With BREAK inside EXCEPT in UK
    FOR    ${i}     IN RANGE    6
        TRY
            Fail    This is excepted!
        EXCEPT    This is excepted!
            BREAK
        ELSE
            Fail    should not be executed
        END
        Fail    should not be executed
    END
    Should be equal    ${i}    ${0}

With BREAK inside TRY-ELSE in UK
    FOR    ${i}     IN RANGE    6
        TRY
            No operation
        EXCEPT    This is excepted!
            Fail    This is excepted!
        ELSE
            BREAK
        END
        Fail    should not be executed
    END
    Should be equal    ${i}    ${0}
