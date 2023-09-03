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

Second matching except ignored
    TRY
        Fail    failure
    EXCEPT    failure
        No operation
    EXCEPT    failure
        Fail    Should not be executed
    END

Except handler failing
    [Documentation]    FAIL    oh no
    TRY
        Fail    GLOB bar
    EXCEPT    GLOB bar
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

Syntax errors cannot be caught
    [Documentation]    FAIL Assign mark '=' can be used only with the last variable.
    TRY
        ${y} =    ${x}     Set Variable
    EXCEPT
        Fail    Should not be run
    ELSE
        Fail    Should not be run
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
    [Documentation]    FAIL oh no, failure again
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
    [Documentation]    FAIL all else fails
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
    [Documentation]    FAIL oh no
    TRY
        FAIL    oh no
    FINALLY
        No operation
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
