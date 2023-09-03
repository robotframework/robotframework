*** Settings ***
Resource        resource.robot

*** Test Cases ***
WHILE
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 2.
    ${i} =    Set variable     ${1}
    WHILE    $i != 5
        Log    ${i}
        Simple UK
        ${i}=    Evaluate     $i + ${1}
    END
    WHILE    $i != 2
        Anarchy in the UK    1    2
    END
    While Loop in UK
    This is validated

WHILE with BREAK and CONTINUE
    ${i} =    Set variable     ${1}
    WHILE    $i != 5
        ${i}=    Evaluate     $i + ${1}
        CONTINUE
    END
    WHILE    True
        BREAK
    END
    This is validated
