*** Variables ***
${expected}    failure
${regexp}      regexp

*** Test Cases ***
Equals is the default matcher
    TRY
        Fail    failure
    EXCEPT    failure
        No operation
    END

Equals with whitespace
    TRY
        Fail    ${SPACE}failure\n\n
    EXCEPT    ${SPACE}failure\n\n
        No operation
    END

Glob matcher
    TRY
        Fail    failure
    EXCEPT    FAI*    type=GloB
        Fail   Should not be executed
    EXCEPT    f*    type=gloB
        No operation
    END

Startswith matcher
    TRY
        Fail    failure
    EXCEPT    fai        type=start
        No operation
    END

Regexp matcher
    TRY
        Fail    failure
    EXCEPT    fai?lu    type=REGEXP
        Fail   Should not be executed
    EXCEPT    fai?lu.*    type=REGEXP
        No operation
    END

Regexp escapes
    TRY
        Fail    000failure
    EXCEPT    \\d\\d\\dfai?lu.*    type=REGEXP
        No operation
    END

Regexp flags
    TRY
        Fail    MESSAGE\nIN\nMANY\nLINES
    EXCEPT    message.*lines    type=REGEXP
        Fail   Should not be executed
    EXCEPT    (?is)message.*lines    type=REGEXP
        No operation
    END

Variable in pattern
    TRY
        Fail    failure
    EXCEPT    ${expected}
        No operation
    END

Invalid variable in pattern
    [Documentation]    FAIL    Variable '${does not exist}' not found.
    TRY
        Fail   Oh no!
    EXCEPT    ${does not exist}
        Fail   Should not be executed
    FINALLY
        Log    finally here
    END

Non-string pattern
    [Documentation]    FAIL    failure
    TRY
        Fail    failure
    EXCEPT    ${42}
        Fail   Should not be executed
    EXCEPT    ${42}    type=glob
        Fail   Should not be executed
    EXCEPT    ${42}    type=regexp
        Fail   Should not be executed
    EXCEPT    ${42}    type=start
        Fail   Should not be executed
    END

Variable in pattern type
    TRY
        Fail    failure
    EXCEPT    fai?lu.*    type=${regexp}
        No operation
    END

Invalid variable in pattern type
    [Documentation]    FAIL    Variable '${does not exist}' not found.
    TRY
        Fail   Oh no!
    EXCEPT    foo    type=${does not exist}
        Fail   Should not be executed
    FINALLY
        Log    finally here
    END

Invalid pattern type
    [Documentation]    FAIL    Invalid EXCEPT pattern type 'invalid', expected 'GLOB', 'LITERAL', 'REGEXP' or 'START'.
    TRY
        Fail   Should not be executed
    EXCEPT    x    type=invalid
        Fail   Should not be executed
    END

Non-string pattern type
    [Documentation]    FAIL    Invalid EXCEPT pattern type '42', expected 'GLOB', 'LITERAL', 'REGEXP' or 'START'.
    TRY
        Fail    failure
    EXCEPT    x    type=${42}
        Fail   Should not be executed
    END

Pattern type multiple times
    [Documentation]    FAIL    Option 'type' allowed only once, got values 'glob' and 'start'.
    TRY
        Fail    failure
    EXCEPT    x    type=glob    type=start
        Fail   Should not be executed
    END

Pattern type without patterns
    TRY
        Fail   oh no
    EXCEPT    type=glob
        No operation
    END

Skip cannot be caught
    [Documentation]    SKIP hello!
    TRY
        SKIP   hello!
    EXCEPT
        No operation
    FINALLY
        No operation
    END

Return cannot be caught
    ${value}=    Uk with return
    Should be equal    ${value}    value

AS gets the message
    TRY
        Fail    failure
    EXCEPT    failure    AS    ${err}
        Should be equal    ${err}    failure
    END

AS with multiple pattern
    TRY
        Fail    failure
    EXCEPT    fa    fa?lur?    type=glob    AS    ${err}
        Should be equal    ${err}    failure
    END

AS with many failures
    TRY
        Run keyword and continue on failure    Fail    oh no!
        Fail    fail again!
    EXCEPT    Several*    type=glob    AS   ${err}
        Should be equal    ${err}    Several failures occurred:\n\n1) oh no!\n\n2) fail again!
    END

AS with default except
    TRY
        Fail    failure
    EXCEPT    AS    ${err}
        Should be equal    ${err}    failure
    END

AS as the error message
    TRY
        Fail    AS
    EXCEPT    \AS    AS    ${err}
        Should be equal    ${err}    \AS
    END

*** Keywords ***
Uk with return
    TRY
        RETURN    value
    EXCEPT    GLOB: *
        Fail    Should not be executed
    FINALLY
        No operation
    END
