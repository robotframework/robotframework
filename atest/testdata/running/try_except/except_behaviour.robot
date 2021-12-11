*** Variables ***
${expected}    failure

*** Test Cases ***
Equals is the default matcher
    TRY
        Fail    failure
    EXCEPT    failure
        No operation
    END

Glob matcher
    TRY
        Fail    failure
    EXCEPT    GLOB: f*
        No operation
    END

Startswith matcher
    TRY
        Fail    failure
    EXCEPT    STARTS: fai
        No operation
    END

Regexp matcher
    TRY
        Fail    failure
    EXCEPT    REGEXP: fai?lu.*
        No operation
    END

Variable in pattern
    TRY
        Fail    failure
    EXCEPT    ${expected}
        No operation
    END

Return cannot be catch
    Uk with return

AS gets the message
    TRY
        Fail    failure
    EXCEPT    failure    AS    ${err}
        Should be equal    ${err}    failure
    END

AS with many failures
    TRY
        Run keyword and continue on failure    Fail    oh no!
        Fail    fail again!
    EXCEPT    GLOB: several*    AS   ${err}
        Should be equal    ${err}    Several failures occurred:\n\n1) oh no!\n\n2) fail again!
    END

AS with default except
    TRY
        Fail    failure
    EXCEPT    AS    ${err}
        Should be equal    ${err}    failure
    END


*** Keywords ***
Uk with return
    TRY
        RETURN
    EXCEPT    GLOB: *
        Fail    Should not be executed
    END
