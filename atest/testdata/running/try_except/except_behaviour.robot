*** Variables ***
${expected}                 failure
${expected_with_pattern}    GLOB: ?

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
    EXCEPT    GLOB: FAI*
        Fail   Should not be executed
    EXCEPT    GLOB: f*
        No operation
    END

Glob with leading whitespace
    TRY
        Fail    ${SPACE}failure
    EXCEPT    GLOB: ${SPACE}f*
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
    EXCEPT    REGEXP: fai?lu
        Fail   Should not be executed
    EXCEPT    REGEXP: fai?lu.*
        No operation
    END

Regexp escapes
    TRY
        Fail    000failure
    EXCEPT    REGEXP: \\d\\d\\dfai?lu.*
        No operation
    END

Regexp flags
    TRY
        Fail    MESSAGE\nIN\nMANY\nLINES
    EXCEPT    REGEXP: message.*lines
        Fail   Should not be executed
    EXCEPT    REGEXP: (?is)message.*lines
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

Matcher type cannot be defined with variable
    [Documentation]    FAIL failure
    TRY
        Fail    GLOB: ?
    EXCEPT    ${expected_with_pattern}
        No operation
    ELSE
        Fail    Should not be executed
    END
    TRY
        Fail    failure
    EXCEPT    ${expected_with_pattern}
        Fail    Should not be executed
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
    EXCEPT    fa    GLOB: fa?lur?    AS    ${err}
        Should be equal    ${err}    failure
    END

AS with many failures
    TRY
        Run keyword and continue on failure    Fail    oh no!
        Fail    fail again!
    EXCEPT    GLOB: Several*    AS   ${err}
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
