*** Test Cases ***
Simple
    Simple

Return value
    ${value} =    Return value
    Should be equal    ${value}    value

Return value as variable
    ${value} =    Return value as variable
    Should be equal    ${value}    ${42}

Return multiple values
    ${x}    ${y}    ${z} =    Return multiple values
    Should be equal    ${x}    first
    Should be equal    ${y}    ${2}
    Should be equal    ${z}    third

In IF
    ${x} =    Return in IF    first
    Should be equal    ${x}    ${1}
    ${x} =    Return in IF    second
    Should be equal    ${x}    ${2}

In inline IF
    ${x} =    Return in inline IF    first
    Should be equal    ${x}    ${1}
    ${x} =    Return in inline IF    second
    Should be equal    ${x}    ${2}

In FOR
    ${x} =    Return in FOR
    Should be equal    ${x}    ${0}

In nested FOR/IF structure
    ${x} =    Return in nested FOR/IF structure
    Should be equal    ${x}    ${6}

In test
    [Documentation]    FAIL 'Return' is a reserved keyword.
    RETURN

In test with values
    [Documentation]    FAIL 'Return' is a reserved keyword.
    RETURN    v1    v2

In test inside IF
    [Documentation]    FAIL Invalid 'RETURN' usage.
    IF    True
        RETURN
    END

In test inside FOR
    [Documentation]    FAIL Invalid 'RETURN' usage.
    FOR    ${x}    IN    whatever
        RETURN
    END

*** Keywords ***
Simple
    Log    Before
    RETURN
    Fail    Not run

Return value
    RETURN    value

Return value as variable
    RETURN    ${42}

Return multiple values
    RETURN    first    ${2}    third

Return in IF
    [Arguments]    ${arg}
    IF    $arg == 'first'
        RETURN    ${1}
        Fail    Not run
    ELSE
        RETURN    ${2}
        Fail    Not run
    END
    Fail    Not run

Return in inline IF
    [Arguments]    ${arg}
    IF    $arg == 'first'    RETURN    ${1}    ELSE    RETURN    ${2}
    Fail    Not run

Return in FOR
    FOR    ${x}    IN RANGE    10
        RETURN    ${x}
        Fail    Not run
    END
    Fail    Not run

Return in nested FOR/IF structure
    IF    True
        FOR    ${x}    IN RANGE    10
            IF    ${x} > 5    RETURN    ${x}
        END
    END
    Fail    Not run
