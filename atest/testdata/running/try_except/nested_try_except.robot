*** Test cases ***
Try except inside if
    IF    True
        TRY
            Fail    nested failure
        EXCEPT    nested failure
            Log    Catch
        END
    END

Try except inside else if
    IF    False
        No operation
    ELSE IF    True
        TRY
            No operation
        EXCEPT    nested failure
            Fail    Should not be here
        ELSE
            Log    in the else branch
        END
    END

Try except inside else
    IF    False
        No operation
    ELSE
        TRY
            Fail    nested failure
        EXCEPT    nested failure
            Log    Catch
        END
    END

Try except inside for loop
   FOR   ${i}    IN    1    2
       TRY
           Should be equal    ${i}    1
       EXCEPT    2 != 1
            Log    catch
       ELSE
            Log    all good
       END
   END

If inside try failing
    TRY
        IF    True
            Fail    Oh no
        ELSE
            No operation
        END
    EXCEPT    Oh no
        No operation
    ELSE
        Fail    Should not be executed
    END

If inside except handler
    TRY
        Fail    Oh no
    EXCEPT    Oh no
        IF    False
            Fail    Should not be executed
        ELSE
            No operation
        END
    ELSE
        Fail    Should not be executed
    END

If inside except handler failing
    [Documentation]    FAIL Oh no again!
    TRY
        Fail    Oh no
    EXCEPT    Oh no
        IF    True
            Fail    Oh no again!
        ELSE
            No operation
        END
    ELSE
        Fail    Should not be executed
    END

If inside else block
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    ELSE
        IF    False
            Fail    Should not be executed
        ELSE
            No operation
        END
    END

If inside else block failing
    [Documentation]    FAIL Oh no
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    ELSE
        IF    False
            No operation
        ELSE
            Fail    Oh no
        END
    END

If inside finally block
    [Documentation]    FAIL cannot catch me
    TRY
        Fail   cannot catch me
    EXCEPT    Oh no
        Fail    Should not be executed
    FINALLY
        IF    False
            Fail    Should not be executed
        ELSE
            No operation
        END
    END

If inside finally block failing
    [Documentation]    FAIL Oh no
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    FINALLY
        IF    False
            No operation
        ELSE
            Fail    Oh no
        END
    END

For loop inside try failing
    TRY
       FOR   ${i}    IN    1    2
           Should be equal    ${i}    1
       END
    EXCEPT    2 != 1
        No operation
    ELSE
        Fail    Should not be executed
    END

For loop inside except handler
    TRY
        Fail    Oh no
    EXCEPT    Oh no
        FOR   ${i}    IN    1    2
            Should be equal    ${i}     ${i}
        END
    ELSE
        Fail    Should not be executed
    END

For loop inside except handler failing
    [Documentation]    FAIL 2 != 1
    TRY
        Fail    Oh no
    EXCEPT    Oh no
        FOR   ${i}    IN    1    2
            Should be equal    ${i}    1
        END
    ELSE
        Fail    Should not be executed
    END

For loop inside else block
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    ELSE
        FOR   ${i}    IN    1    2
            Should be equal    ${i}     ${i}
        END
    END

For loop inside else block failing
    [Documentation]    FAIL 2 != 1
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    ELSE
        FOR   ${i}    IN    1    2
            Should be equal    ${i}    1
        END
    END

For loop inside finally block
    [Documentation]    FAIL cannot catch me
    TRY
        Fail   cannot catch me
    EXCEPT    Oh no
        Fail    Should not be executed
    FINALLY
        FOR   ${i}    IN    1    2
            Should be equal    ${i}    ${i}
        END
    END

For loop inside finally block failing
    [Documentation]    FAIL 2 != 1
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    FINALLY
        FOR   ${i}    IN    1    2
            Should be equal    ${i}    1
        END
    END
