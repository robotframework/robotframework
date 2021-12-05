*** Test Cases ***
Try with no failures
    Try with no failures

First except executed
    First except executed

Second except executed
    Second except executed

Second matching except ignored
    Second matching except ignored

Except handler failing
    [Documentation]    FAIL    oh no
    Except handler failing

Else branch executed
    Else branch executed

Else branch not executed
    Else branch not executed

Else branch failing
    [Documentation]    FAIL oh noes, a catastrophe
    Else branch failing

Multiple except patterns
    Multiple except patterns

Default except pattern
    Default except pattern

Finally block executed when no failures
    Finally block executed when no failures

Finally block executed after catch
    Finally block executed after catch

Finally block executed after failure in except
    [Documentation]    FAIL oh no, failure again
    Finally block executed after failure in except

Finally block executed after failure in else
    [Documentation]    FAIL all else fails
    Finally block executed after failure in else

Try finally with no errors
    Try finally with no errors

Try finally with failing try
    [Documentation]    FAIL oh no
    Try finally with failing try

Finally block failing
    [Documentation]    FAIL fail in finally
    Finally block failing

Return in try
    Return in try

Return in except handler
    Return in except handler

Return in else
    Return in else

*** Keywords ***
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

Second matching except ignored
    TRY
        Fail    failure
    EXCEPT    failure
        No operation
    EXCEPT    failure
        Fail    Should not be executed
    END

Except handler failing
    TRY
        Fail    bar
    EXCEPT    bar
        Fail   oh no
    ELSE
        Fail    should not be executed
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
    ELSE
        Log    in the else
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

Finally block executed after failure in except
    TRY
        Fail    all not good
    EXCEPT    all not good
        Fail    oh no, failure again
    ELSE
        Fail    should not be executed
    FINALLY
        Log    Hello from finally!
    END

Finally block executed after failure in else
    TRY
        No operation
    EXCEPT    all not good
        Fail    should not be executed
    ELSE
        Fail    all else fails
    FINALLY
        Log    Hello from finally!
    END

Try finally with no errors
    TRY
        No operation
    FINALLY
        No operation
    END

Try finally with failing try
    TRY
        FAIL    oh no
    FINALLY
        No operation
    END

Finally block failing
    TRY
        Fail    all not good
    EXCEPT    all not good
        Log    we are safe now
    FINALLY
        Fail    fail in finally
    END

Return in try
    TRY
        RETURN    1
    EXCEPT    foo
        Fail    should not be executed
    ELSE
        Fail    should not be executed
    FINALLY
        Log    finally is always executed
    END

Return in except handler
    TRY
        Fail    foo
    EXCEPT    foo
        RETURN    1
    ELSE
        Fail    should not be executed
    FINALLY
        Log    finally is always executed
    END

Return in else
    TRY
        No operation
    EXCEPT    foo
        Fail    should not be executed
    ELSE
        RETURN    1
    FINALLY
        Log    finally is always executed
    END
