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

No condition
    WHILE
        ${variable}=    Evaluate    $variable + 1
        IF    ${variable} > 5
            BREAK
        END
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
        Log    ${variable}
    END

Continuable failure in loop
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Oh no 1!
    ...
    ...    2) Oh no 2!
    ...
    ...    3) Oh no 3!
    ...
    ...    4) Oh no outside loop!
    [Tags]    robot:continue-on-failure
    WHILE    $variable < 4
        Fail    Oh no ${variable}!
        ${variable}=    Evaluate    $variable + 1
    END
    Fail    Oh no outside loop!

Normal failure after continuable failure in loop
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Oh no!
    ...
    ...    2) Oh no for real!
    WHILE    True
        IF    $variable > 1    Fail    Oh no for real!
        Run Keyword And Continue On Failure    Fail    Oh no!
        ${variable}=    Evaluate    $variable + 1
    END

Normal failure outside loop after continuable failures in loop
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Oh no 1!
    ...
    ...    2) Oh no 2!
    ...
    ...    3) Oh no for real!
    WHILE    $variable < 3
        Run Keyword And Continue On Failure    Fail    Oh no ${variable}!
        ${variable}=    Evaluate    $variable + 1
    END
    Fail    Oh no for real!
    Fail    Should not be executed.

Loop in loop
    WHILE    $variable < 6
        Log    Outer ${variable}
        ${i}=    Set variable    ${3}
        WHILE    $i > 0
            Log    Inner ${i}
            ${i}=    Evaluate    $i - 1
        END
        ${variable}=    Evaluate    $variable + 1
    END

In keyword
    While keyword

Loop fails in keyword
    [Documentation]    FAIL 2 != 1
    Failing while keyword

With RETURN
    While with RETURN

Condition evaluation time is included in elapsed time
    WHILE    ${{time.sleep(0.1)}} or ${variable}
        ${variable}=    Evaluate    $variable - 1
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
