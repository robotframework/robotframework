*** Settings ***
Resource           lineno_and_source.resource

*** Test Cases ***
Keyword
    No Operation

User keyword
    User Keyword

User keyword in resource
    User Keyword In Resource

Not run keyword
    [Documentation]    FAIL    This fails
    Fail    This fails
    Fail    Not run
    Non-existing

FOR
    FOR    ${x}    IN    first    second
        No Operation
    END

FOR in keyword
    FOR In keyword

FOR in IF
    IF    True
        FOR    ${x}    ${y}    IN    x    y
            No Operation
        END
    END

FOR in resource
    FOR In resource

IF
    IF    1 > 2
        Fail    Should not be executed
    ELSE IF    1 < 2
        No Operation
    ELSE
        Fail    Should not be executed
    END

IF in keyword
    IF In keyword

IF in FOR
    [Documentation]    FAIL    2
    FOR    ${x}    IN    1    2
        IF    ${x} == 1
            Log    ${x}
        ELSE
            Fail    ${x}
        END
    END

IF in resource
    IF In resource

*** Keywords ***
User Keyword
    No Operation

FOR In Keyword
    FOR    ${x}    IN    once
        No Operation
    END

IF In Keyword
    IF    True
        No Operation
    END
