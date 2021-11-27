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
    EXCEPT    does not match
            Fail    Should not be executed
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

Finally block executed when no failures
    TRY
        Log    all good
    EXCEPT
        Fail    should not be executed
    FINALLY
        Log    Hello from finally!
    END

Finally block executed after catch
    TRY
        Fail    all not good
    EXCEPT    all not good
        Log    we are safe now
    FINALLY
        Log    Hello from finally!
    END

Finally block failing
    [Documentation]    FAIL fail in finally
    TRY
        Fail    all not good
    EXCEPT    all not good
        Log    we are safe now
    FINALLY
        Fail    fail in finally
    END
