*** Settings ***
Documentation     This suite tries to cover all possible syntax.
...
...               It can be used for testing different output files etc.
...               Features themselves are tested more thoroughly elsewhere.
Metadata          Name    Value
Suite Setup       Log    Library keyword
Suite Teardown    User Keyword
Resource          failing_import_creates_error.resource

*** Test Cases ***
Library keyword
    Log    Library keyword

User keyword and RETURN
    ${value} =    User Keyword    value
    Should Be Equal    ${value}    return value

Test documentation, tags and timeout
    [Documentation]    Hello, world!
    [Tags]    hello    world
    [Timeout]    1 min
    No Operation

Test setup and teardown
    [Setup]    Log    Library keyword
    Log    Body
    [Teardown]    User Keyword

Keyword Keyword documentation, tags and timeout
    Keyword documentation, tags and timeout

Keyword setup and teardown
    Keyword setup and teardown

Failure
    [Documentation]    FAIL    Expected!
    Fail    Expected!
    Fail    Not run

VAR
    VAR    ${x}    x    scope=SUITE

IF
    IF    $x == 'y'
        Fail    Not run
    ELSE IF    $x == 'x'
        Log    Hi!
    ELSE
        Fail    Not run
    END

TRY
    TRY
        Fail    Hello!
    EXCEPT    no    match    here
        Fail    Not run
    EXCEPT    *!    type=GLOB    AS    ${err}
        Should Be Equal    ${err}    Hello!
    ELSE
        Fail    Not run
    FINALLY
        Log    Finally in FINALLY
    END

FOR and CONTINUE
    FOR    ${x}    IN    a    b    c
        IF    $x in ['a', 'c']    CONTINUE
        Should Be Equal    ${x}    b
    END
    FOR    ${i}    ${x}    IN ENUMERATE    x    start=1
        Should Be Equal    ${x}${i}    x1
    END
    FOR    ${i}    ${x}    IN ZIP    ${{[]}}    ${{['x']}}    mode=LONGEST    fill=1
        Should Be Equal    ${x}${i}    x1
    END

WHILE and BREAK
    WHILE    True
        BREAK
    END
    WHILE    limit=1    on_limit=PASS    on_limit_message=xxx
        Log    Run once
    END

GROUP
    GROUP    Named
        Log    Hello!
    END
    GROUP
        Log    Hello, again!
    END

Syntax error
    [Documentation]    FAIL    Non-existing setting 'Bad'.
    [Bad]      Setting
    [Ooops]    I did it again

*** Keywords ***
User keyword
    [Arguments]    ${arg}=value
    Should Be Equal    ${arg}    value
    RETURN    return ${arg}

Keyword documentation, tags and timeout
    [Documentation]    Hello, world!
    [Tags]    hello    world
    [Timeout]    1 day
    No Operation

Keyword setup and teardown
    [Setup]    Log    Library keyword
    Log    Body
    [Teardown]    User Keyword
