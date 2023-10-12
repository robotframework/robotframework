*** Test Cases ***
CONTINUE
    FOR    ${i}    IN     2     3     4
        CONTINUE
        Fail    should not be executed
    END

CONTINUE inside IF
    [Documentation]    FAIL Oh no, got 4
    FOR    ${i}     IN RANGE    6
        IF    $i == 4
            Fail    Oh no, got 4
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

CONTINUE inside TRY
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

CONTINUE inside EXCEPT and TRY-ELSE
    FOR    ${i}     IN RANGE    6
        TRY
            Should not be equal    ${i}    ${4}
        EXCEPT    AS    ${error}
            Log    ${error}
            CONTINUE
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

BREAK
    FOR    ${i}     IN RANGE    1000
        BREAK
        Fail    should not be executed
    END
    Should be equal    ${i}    ${0}

BREAK inside IF
    FOR    ${i}     IN RANGE    6
        IF    $i == 3
            BREAK
            Fail    should not be executed
        END
    END

BREAK inside TRY
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

BREAK inside EXCEPT
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

BREAK inside TRY-ELSE
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

CONTINUE in UK
    CONTINUE in UK

CONTINUE inside IF in UK
    [Documentation]    FAIL Oh no, got 4
    CONTINUE inside IF in UK

CONTINUE inside TRY in UK
    CONTINUE inside TRY in UK

CONTINUE inside EXCEPT and TRY-ELSE in UK
    CONTINUE inside EXCEPT and TRY-ELSE in UK

BREAK in UK
    BREAK in UK

BREAK inside IF in UK
    BREAK inside IF in UK

BREAK inside TRY in UK
    BREAK inside TRY in UK

BREAK inside EXCEPT in UK
    BREAK inside EXCEPT in UK

BREAK inside TRY-ELSE in UK
    BREAK inside TRY-ELSE in UK

*** Keywords ***
CONTINUE in UK
    FOR    ${i}    IN     2     3     4
        CONTINUE
        Fail    should not be executed
    END

CONTINUE inside IF in UK
    [Documentation]    FAIL Oh no, got 4
    FOR    ${i}     IN RANGE    6
        IF    $i == 4
            Fail    Oh no, got 4
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

CONTINUE inside TRY in UK
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

CONTINUE inside EXCEPT and TRY-ELSE in UK
    FOR    ${i}     IN RANGE    6
        TRY
            Should not be equal    ${i}    ${4}
        EXCEPT    AS    ${error}
            Log    ${error}
            CONTINUE
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

BREAK in UK
    FOR    ${i}     IN RANGE    1000
        BREAK
        Fail    should not be executed
    END
    Should be equal    ${i}    ${0}

BREAK inside IF in UK
    FOR    ${i}     IN RANGE    6
        IF    $i == 3
            BREAK
            Fail    should not be executed
        END
    END

BREAK inside TRY in UK
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

BREAK inside EXCEPT in UK
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

BREAK inside TRY-ELSE in UK
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
