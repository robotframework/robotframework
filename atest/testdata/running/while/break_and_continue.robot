*** Variables ***
${variable}    ${1}

*** Test Cases ***
With CONTINUE
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        CONTINUE
        Fail    should not be executed
    END

With CONTINUE inside IF
    [Documentation]    FAIL Oh no, got 4
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        IF    $variable == 4
            Fail    Oh no, got 4
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

With CONTINUE inside TRY
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        TRY
            CONTINUE
            Fail    should not be executed
        EXCEPT
            Fail    should not be executed
        ELSE
            Log     all is fine!
        END
    END

With CONTINUE inside EXCEPT and TRY-ELSE
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        TRY
            Should not be equal    ${variable}    ${4}
        EXCEPT
            CONTINUE
        ELSE
            CONTINUE
        END
        Fail    should not be executed
    END

With BREAK
    WHILE    True
        BREAK
        ${variable}=    Evaluate    $variable + 1
    END
    Should be equal    ${variable}    ${1}

With BREAK inside IF
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        IF    $variable == 3
            BREAK
            Fail    should not be executed
        END
    END

With BREAK inside TRY
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        TRY
            BREAK
            Fail    should not be executed
        EXCEPT
            Fail    should not be executed
        ELSE
            Fail    should not be executed
        END
        Fail    should not be executed
    Should be equal    ${variable}    ${2}
    END

With BREAK inside EXCEPT
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        TRY
            Fail    This is excepted!
        EXCEPT    This is excepted!
            BREAK
        ELSE
            Fail    should not be executed
        END
        Fail    should not be executed
    Should be equal    ${variable}    ${2}
    END

With BREAK inside TRY-ELSE
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        TRY
            No operation
        EXCEPT    This is excepted!
            Fail    This is excepted!
        ELSE
            BREAK
        END
        Fail    should not be executed
    Should be equal    ${variable}    ${2}
    END

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
