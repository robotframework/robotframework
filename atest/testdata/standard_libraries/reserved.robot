*** Test Case ***
For
    [Documentation]    FAIL 'For' is a reserved keyword
    For    item    in    list

Continue
    [Documentation]    FAIL 'Continue' is a reserved keyword
    No Operation
    Continue

Reserved in User Keyword
    [Documentation]    FAIL 'While' is a reserved keyword
    User keyword with reserved keyword

Else should be capitalized
    [Documentation]     FAIL 'else' is a reserved keyword. 'else' must be in uppercase (ELSE) when used as a marker with 'Run Keyword If'.
    ELSE    log   log something

Else If should be capitalized
    [Documentation]     FAIL 'else if' is a reserved keyword. 'else if' must be in uppercase (ELSE IF) when used as a marker with 'Run Keyword If'.
    ELSE IF    log   log something

*** Keyword ***
User keyword with reserved keyword
    While
