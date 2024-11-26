*** Settings ***
Test Template     Run Keyword

*** Test Cases ***
SKIP + PASS -> PASS
    Skip    Skipped
    Log     Passed

FAIL + ANY -> FAIL
    [Documentation]    FAIL    Failed
    Log     Passed
    Skip    Skipped
    Log     Passed
    Fail    Failed
    Skip    Skipped

Only SKIP -> SKIP
    [Documentation]    SKIP    All iterations skipped.
    Skip    Skipped
    Skip    Skipped

IF w/ SKIP + PASS -> PASS
    IF    True
        Skip    Skipped
        Log     Passed
    ELSE
        Fail    Not executed
    END
    IF    True    Skip    Skipped
    IF    True    Log     Passed

IF w/ FAIL + ANY -> FAIL
    [Documentation]    FAIL    Failed
    IF    False
        Fail    Not executed
    ELSE
        Log     Passed
        Skip    Skipped
        Log     Passed
        Fail    Failed
        Skip    Skipped
    END
    IF    True    Skip    Skipped
    IF    True    Log     Passed

IF w/ only SKIP -> SKIP
    [Documentation]    SKIP    All iterations skipped.
    IF    True
        Skip    Skip 1
        Skip    Skip 2
    END
    IF    True    Skip    Skip 3
    IF    True    Skip    Skip 4

FOR w/ SKIP + PASS -> PASS
    FOR    ${x}    IN    a    b
        Skip    ${x}
        Log     ${x}
    END
    FOR    ${x}    IN    just once
        Skip    ${x}
    END
    FOR    ${x}    IN    just once
        Skip    ${x}
        Log     ${x}
    END

FOR w/ FAIL + ANY -> FAIL
    [Documentation]    FAIL    Several failures occurred:\n\n1) a\n\n2) b
    FOR    ${x}    IN    a   b
        Skip    ${x}
        Fail    ${x}
        Log     ${x}
    END
    FOR    ${x}    IN    just once
        Skip    ${x}
    END
    FOR    ${x}    IN    just once
        Skip    ${x}
        Log     ${x}
    END

FOR w/ only SKIP -> SKIP
    [Documentation]    SKIP    All iterations skipped.
    FOR    ${x}    IN    a   b
        Skip    ${x} 1
        Skip    ${x} 2
    END
    FOR    ${x}    IN    just once
        Skip    ${x}
    END
