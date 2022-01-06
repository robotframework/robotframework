*** Test cases ***
Try except inside try
    TRY
        TRY
            Fail    nested failure
        EXCEPT    miss
            Fail    Should not be executed
        ELSE
            No operation
        FINALLY
            Log    in the finally
        END
    EXCEPT    nested failure
        No operation
    END

Try except inside except
    TRY
        Fail    oh no!
    EXCEPT    oh no!
        TRY
            Fail    nested failure
        EXCEPT    nested failure
            No operation
        FINALLY
            Log    in the finally
        END
    ELSE
        Fail    Should not be executed
    END

Try except inside try else
    TRY
        No operation
    EXCEPT    oh no!
        Fail    Should not be executed
    ELSE
        TRY
            Fail    nested failure
        EXCEPT    nested failure
            No operation
        FINALLY
            Log    in the finally
        END
    END

Try except inside finally
    TRY
        Fail    oh no!
    EXCEPT    oh no!
        No operation
    FINALLY
        TRY
            Fail    nested failure
        EXCEPT    nested failure
            No operation
        FINALLY
            Log    in the finally
        END
    END

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

Try except inside while loop
    ${i}=    Set variable   ${1}
    WHILE   $i < 3
       TRY
           Should be equal    ${i}    ${1}
       EXCEPT    2 != 1
            Log    catch
       ELSE
            Log    all good
       END
       ${i}=    Evaluate    $i + 1
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

While loop inside try failing
    TRY
        ${i}=    Set variable   ${1}
        WHILE   $i < 3
            Should be equal    ${i}    ${1}
            ${i}=    Evaluate   $i + 1
        END
    EXCEPT    2 != 1
        No operation
    ELSE
        Fail    Should not be executed
    END

While loop inside except handler
    TRY
        Fail    Oh no
    EXCEPT    Oh no
        ${i}=    Set variable   ${1}
        WHILE   $i < 3
            Should be equal    ${i}    ${i}
            ${i}=    Evaluate   $i + 1
        END
    ELSE
        Fail    Should not be executed
    END

While loop inside except handler failing
    [Documentation]    FAIL 2 != 1
    TRY
        Fail    Oh no
    EXCEPT    Oh no
        ${i}=    Set variable   ${1}
        WHILE   $i < 3
            Should be equal    ${i}    ${1}
            ${i}=    Evaluate   $i + 1
        END
    ELSE
        Fail    Should not be executed
    END

While loop inside else block
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    ELSE
        ${i}=    Set variable   ${1}
        WHILE   $i < 3
            Should be equal    ${i}    ${i}
            ${i}=    Evaluate   $i + 1
        END
    END

While loop inside else block failing
    [Documentation]    FAIL 2 != 1
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    ELSE
        ${i}=    Set variable   ${1}
        WHILE   $i < 3
            Should be equal    ${i}    ${1}
            ${i}=    Evaluate   $i + 1
        END
    END

While loop inside finally block
    [Documentation]    FAIL cannot catch me
    TRY
        Fail   cannot catch me
    EXCEPT    Oh no
        Fail    Should not be executed
    FINALLY
        ${i}=    Set variable   ${1}
        WHILE   $i < 3
            Should be equal    ${i}    ${i}
            ${i}=    Evaluate   $i + 1
        END
    END

While loop inside finally block failing
    [Documentation]    FAIL 2 != 1
    TRY
        No operation
    EXCEPT    Oh no
        Fail    Should not be executed
    FINALLY
        ${i}=    Set variable   ${1}
        WHILE   $i < 3
            Should be equal    ${i}    ${1}
            ${i}=    Evaluate   $i + 1
        END
    END

Try Except in test setup
    [Setup]    Passing uk with try except
    No operation

Try Except in test teardown
    [Teardown]    Passing uk with try except
    No operation

Failing Try Except in test setup
    [Documentation]    FAIL Setup failed:\nOh no
    [Setup]    Failing uk with try except
    No operation

Failing Try Except in test teardown
    [Documentation]    FAIL Teardown failed:\nOh no
    [Teardown]    Failing uk with try except
    No operation

Failing Try Except in test teardown and other failures
    [Documentation]    FAIL failure in body\n\nAlso teardown failed:\nOh no
    [Teardown]    Failing uk with try except
    Fail    failure in body

*** Keywords ***
Passing uk with try except
    TRY
        Fail    Oh no
    EXCEPT    Oh no
        No operation
    END

Failing uk with try except
    TRY
        Fail    Oh no
    EXCEPT    Oh no no oh!
        No operation
    END
