*** Variables ***
${variable}    ${1}

*** Test Cases ***
While loop executed once
    WHILE    $variable < 2
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

While loop executed multiple times
    WHILE    $variable < 6
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

While loop not executed
    WHILE    $variable > 2
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

While loop execution fails on the first loop
    [Documentation]    FAIL Oh no
    WHILE    $variable < 2
        Fail    Oh no
    END

While loop execution fails after some loops
    [Documentation]    FAIL Oh no, got 4
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        IF    $variable == 4
            Fail    Oh no, got 4
        END
    END
