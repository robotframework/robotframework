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
    END
    Should be equal    ${variable}    ${2}

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
    END
    Should be equal    ${variable}    ${2}

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
    END
    Should be equal    ${variable}    ${2}

BREAK with continuable failures
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Failure
    ...
    ...    2) Another failure
    [Tags]    robot:continue-on-failure
    WHILE    True
        Fail    Failure
        Fail    Another failure
        BREAK
        Fail    Not run
    END

CONTINUE with continuable failures
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Failure 1
    ...
    ...    2) Failure 0
    WHILE    $variable >= 0
        Run Keyword And Continue On Failure    Fail    Failure ${variable}
        ${variable} =    Set Variable    ${variable - 1}
        CONTINUE
        Fail    Not run
    END

Invalid BREAK
    [Documentation]    FAIL    BREAK does not accept arguments, got 'bad'.
    WHILE   True
        BREAK    bad
    END

Invalid CONTINUE
    [Documentation]    FAIL    CONTINUE does not accept arguments, got 'bad'.
    WHILE   True
        CONTINUE    bad
    END

Invalid BREAK not executed
    WHILE   True
        IF    False
            BREAK    bad
        ELSE
            BREAK
        END
    END

Invalid CONTINUE not executed
    WHILE   False
        CONTINUE    bad
    END

With CONTINUE in UK
    With CONTINUE in UK

With CONTINUE inside IF in UK
    [Documentation]    FAIL Oh no, got 4
    With CONTINUE inside IF in UK

With CONTINUE inside TRY in UK
    With CONTINUE inside TRY in UK

With CONTINUE inside EXCEPT and TRY-ELSE in UK
    With CONTINUE inside EXCEPT and TRY-ELSE in UK

With BREAK in UK
    With BREAK in UK

With BREAK inside IF in UK
    With BREAK inside IF in UK

With BREAK inside TRY in UK
    With BREAK inside TRY in UK

With BREAK inside EXCEPT in UK
    With BREAK inside EXCEPT in UK

With BREAK inside TRY-ELSE in UK
    With BREAK inside TRY-ELSE in UK

*** Keywords ***
With CONTINUE in UK
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        CONTINUE
        Fail    should not be executed
    END

With CONTINUE inside IF in UK
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

With CONTINUE inside TRY in UK
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

With CONTINUE inside EXCEPT and TRY-ELSE in UK
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

With BREAK in UK
    WHILE    True
        BREAK
        Fail    should not be executed
    END
    Should be equal    ${variable}    ${1}

With BREAK inside IF in UK
    WHILE    $variable < 6
        ${variable}=    Evaluate    $variable + 1
        IF    $variable == 3
            BREAK
            Fail    should not be executed
        END
    END

With BREAK inside TRY in UK
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
    END
    Should be equal    ${variable}    ${2}

With BREAK inside EXCEPT in UK
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
    END
    Should be equal    ${variable}    ${2}

With BREAK inside TRY-ELSE in UK
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
    END
    Should be equal    ${variable}    ${2}
