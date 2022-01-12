*** Settings ***
Resource        resource.robot

*** Test Cases ***
TRY
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 2.
    TRY
        Simple UK
    EXCEPT
        Log    handling it
    ELSE
        Log    in the else
    FINALLY
        Log    in the finally
    END
    TRY
        Anarchy in the UK    1    2
    EXCEPT    GLOB: .*
        Simple UK
    END
    Try except in UK
    This is validated

*** Keywords ***
Try except in UK
    TRY
        Simple UK
    EXCEPT
        Log    handling it
    END
