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

TRY
    [Documentation]    FAIL    Hello, Robot!
    TRY
        Fail    Robot
    EXCEPT    AS    ${name}
        TRY
            Fail    Hello, ${name}!
        FINALLY
            Should Be Equal    ${name}    Robot
        END
    ELSE
        Fail    Not executed
    END

TRY in keyword
    TRY in keyword

TRY in resource
    TRY in resource

Run Keyword
    Run Keyword    Log    Hello
    Run Keyword If    True
    ...    User Keyword

Run Keyword in keyword
    Run Keyword in keyword

Run Keyword in resource
    Run Keyword in resource

In setup and teardown
    [Setup]    User Keyword
    No operation
    [Teardown]    Run Keyword    Log    Hello!

*** Keywords ***
User Keyword
    No Operation
    RETURN

FOR In Keyword
    FOR    ${x}    IN    once
        No Operation
    END

IF In Keyword
    IF    True
        No Operation
        RETURN
    END

TRY In Keyword
    TRY
        RETURN    Value
        Fail    Not executed!
    EXCEPT    No match    AS    ${var}
        Fail    Not executed!
    EXCEPT    No    Match    2    AS    ${x}
        Fail    Not executed!
    EXCEPT
        Fail    Not executed!
    END

Run Keyword in keyword
    Run Keyword    No Operation
