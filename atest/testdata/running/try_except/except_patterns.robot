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
