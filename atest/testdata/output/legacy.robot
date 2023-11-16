*** Settings ***
Documentation        Something...
Metadata             Name    Value
Suite Setup          Log    Hello!

*** Test Cases ***
Passing
    [Documentation]    Something...
    [Tags]    t1    t2
    [Setup]    Passing
    Passing
    [Teardown]    Passing

Failing
    [Documentation]    FAIL    Hello!
    Failing

Failing setup
    [Documentation]    FAIL    Setup failed:\nHello!
    [Setup]    Failing
    Passing

Failing teardown
    [Documentation]    FAIL    Teardown failed:\nHello!
    Passing
    [Teardown]    Failing

Controls
    Controls

Embedded
    Embedded

Warning
    Log    xxx    WARN

*** Keywords ***
Passing
    Log    Hello!

Failing
    Fail    Hello!

Controls
    FOR    ${x}    IN RANGE    5
        IF    ${x} > 1    CONTINUE
        Log    ${x}
    END
    WHILE    True
        BREAK
    END
    RETURN

Em${bed}ded
    Should Be Equal    ${bed}    bed
