*** Variables ***
${variable}    ${1}

*** Test Cases ***
Loop executed once
    WHILE    $variable < 2
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

Loop executed multiple times
    WHILE    $variable < 6
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

Loop not executed
    WHILE    $variable > 2
        Fail    Not executed!
        Not executed either
    END

Execution fails on the first loop
    [Documentation]    FAIL Oh no
    WHILE    $variable < 2
        Fail    Oh no
    END

Execution fails after some loops
    [Documentation]    FAIL Oh no, got 4
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        IF    $variable == 4
            Fail    Oh no, got 4
        END
    END

In keyword
    While keyword

Loop fails in keyword
    [Documentation]    FAIL 2 != 1
    Failing while keyword

With RETURN
    While with RETURN

*** Keywords ***
While keyword
    WHILE    $variable < 4
        ${variable}=    Evaluate    $variable + 1
    END

Failing while keyword
    WHILE    $variable < 4
        Should be equal    ${variable}    ${1}
        ${variable}=    Evaluate    $variable + 1
    END

While with RETURN
    WHILE    True
        RETURN    123
    END
