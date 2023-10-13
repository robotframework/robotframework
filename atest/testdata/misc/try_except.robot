*** Test Cases ***
Everything
    TRY
        Keyword
    EXCEPT    No match    type=glob
        Fail    Not executed
        Fail    Not executed either
    EXCEPT    Ooops!    AS    ${err}
        IF    $err == 'Ooops!'
            Log    Didn't do it again.
        ELSE
            Fail    Ooops, I did it again!
        END
     ELSE
        Fail    Not executed
     FINALLY
        Log    Finally we are in FINALLY!
     END

*** Keywords ***
Keyword
    TRY
        FOR    ${msg}    IN    Ooops!    Auts!
            Fail    ${msg}
        END
    EXCEPT    No match    No match either
        Fail    Not executed
    ELSE
        Fail    Not executed
    END
    IF    True
        TRY
            No Operation
        FINALLY
            No Operation
        END
    END
    FOR    ${error}    IN    First    Second    Third
        TRY
            Fail    ${x}
        EXCEPT    First    Second    Third
            No Operation
        END
    END
