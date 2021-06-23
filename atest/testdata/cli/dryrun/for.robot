*** Settings ***
Resource        resource.robot

*** Test Cases ***
FOR
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 2.
    FOR    ${i}    IN    a    b    c
        Log    ${i}
        Simple UK
    END
    FOR    ${a}    ${b}    IN    a    b    c    d
        Anarchy in the UK    1    2
    END
    For Loop in UK
    This is validated

FOR IN RANGE
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 2.
    FOR    ${i}    IN RANGE    10
        Log    ${i}
        Simple UK
    END
    FOR    ${a}    ${b}    IN RANGE    ${NONE}
        Anarchy in the UK    1    2
    END
    This is validated

FOR IN ENUMERATE
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 2.
    FOR    ${i}    IN ENUMERATE    a    b    c
        Log    ${i}
        Simple UK
    END
    FOR    ${a}    ${b}    IN ENUMERATE    a    b    c    d
        Anarchy in the UK    1    2
    END
    This is validated

FOR IN ZIP
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 2.
    FOR    ${i}    IN ZIP    ${x}    ${y}
        Log    ${i}
        Simple UK
    END
    FOR    ${a}    ${b}    IN ZIP    ${x}    ${y}
        Anarchy in the UK    1    2
    END
    This is validated
