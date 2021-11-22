*** Test Cases ***
Try with no failures
    TRY
        No operation
    EXCEPT    failure
        Fail    Should not be executed
    END

First except executed
    TRY
        Fail    failure
    EXCEPT    failure
        No operation
    END

Second except executed
    TRY
        Fail    failure
    EXCEPT    should not match
        Fail    Should not be executed
    EXCEPT    failure
        No operation
    END

Except handler failing
    [Documentation]    FAIL    oh no
    TRY
        Fail    bar
    EXCEPT    bar
        Fail   oh no
    END

Else branch executed
    TRY
        Log    bar
    EXCEPT    bar
        Fail   should not be executed
    ELSE
        Log   Hello from else branch
    END

Else branch not executed
    TRY
        Fail    bar
    EXCEPT    bar
        Log    Catch!
    ELSE
        Fail   should not be executed
    END

Else branch failing
    [Documentation]    FAIL oh noes, a catastrophe
    TRY
        Log    bar
    EXCEPT    bar
        Fail   should not be executed
    ELSE
        Fail    oh noes, a catastrophe
    END

Multiple except patterns
    TRY
        Fail    bar
    EXCEPT    foo    bar
        Log   Catch it!
    END

Default except pattern
    TRY
        Fail    Failure
    EXCEPT
        Log   Catch it again!
    END
