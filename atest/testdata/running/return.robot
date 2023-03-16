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
    ${result} =    Return multiple values
    Should be true    ${result} == ['first', 2, 'third']

In nested keyword
    ${result} =    Return in nested keyword
    Should be equal    ${result}    Hello, world!

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
    [Documentation]    FAIL RETURN is not allowed in this context.
    RETURN

In test with values
    [Documentation]    FAIL RETURN is not allowed in this context.
    RETURN    v1    v2

In test inside IF
    [Documentation]    FAIL RETURN can only be used inside a user keyword.
    IF    True
        RETURN
    END

In test inside FOR
    [Documentation]    FAIL RETURN can only be used inside a user keyword.
    FOR    ${x}    IN    whatever
        RETURN
    END

In test inside WHILE
    [Documentation]    FAIL RETURN can only be used inside a user keyword.
    WHILE    True
        RETURN
    END

In test inside TRY
    [Documentation]    FAIL RETURN can only be used inside a user keyword.
    TRY
        RETURN
    EXCEPT
        Fail    should not be executed
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

Return in nested keyword
    ${result} =    Nested keyword
    Should be equal    ${result}    Hello, world!
    RETURN    ${result}

Nested keyword
    ${result} =    Nested keyword 2
    RETURN    Hello, ${result}!

Nested keyword 2
    RETURN    world

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
