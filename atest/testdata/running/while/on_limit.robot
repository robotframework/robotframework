*** Variables ***
${variable}    ${1}
${limit}       11
${number}      ${0.2}
${pass}        Pass
${errorMsg}    Error Message
${USE LIMIT}   Use the 'limit' argument to increase or remove the limit if needed.

*** Test Cases ***
On limit pass with time limit defined
    WHILE    True    limit=0.1s    on_limit=${pass}
        No Operation
        Sleep    0.05
    END

On limit pass with iteration limit defined
    WHILE    True    limit=5    on_limit=pass
        No Operation
    END

On limit fail
    [Documentation]    FAIL WHILE loop was aborted because it did not finish within the limit of 5 iterations. ${USE LIMIT}
    WHILE    True    limit=5    on_limit=FaIl
        No Operation
    END

On limit pass with failures in loop
    [Documentation]    FAIL Oh no!
    WHILE    True    limit=5    on_limit=pass
        Fail   Oh no!
    END

On limit pass with continuable failure
    [Documentation]    FAIL Several failures occurred:
    ...
    ...   1) Continuable failure!
    ...
    ...   2) Continuable failure!
    ...
    ...   3) One more failure!
    [Tags]    robot:continue-on-failure
    WHILE    limit=2    on_limit=pass
        Fail    Continuable failure!
    END
    Fail    One more failure!

On limit fail with continuable failure
    [Documentation]    FAIL Several failures occurred:
    ...
    ...   1) Continuable failure!
    ...
    ...   2) Continuable failure!
    ...
    ...   3) WHILE loop was aborted because it did not finish within the limit of 2 iterations. ${USE LIMIT}
    ...
    ...   4) One more failure!
    [Tags]    robot:continue-on-failure
    WHILE    limit=2    on_limit=fail
        Fail    Continuable failure!
    END
    Fail    One more failure!

Invalid on_limit
    [Documentation]    FAIL WHILE option 'on_limit' does not accept value 'inValid'. Valid values are 'PASS' and 'FAIL'.
    WHILE    True    limit=5    on_limit=inValid
        Fail   Should not be executed
    END

Invalid on_limit from variable
    [Documentation]    FAIL Invalid WHILE loop 'on_limit' value: Value 'inValid' is not accepted. Valid values are 'PASS' and 'FAIL'.
    WHILE    True    limit=5    on_limit=${{'inValid'}}
        Fail   Should not be executed
    END

On limit without limit defined
    [Documentation]    FAIL WHILE option 'on_limit' cannot be used without 'limit'.
    WHILE    True    on_limit=PaSS
        Fail   Should not be executed
    END

On limit with invalid variable
    [Documentation]    FAIL Invalid WHILE loop 'on_limit' value: Variable '\${does not exist}' not found.
    WHILE    True    limit=5    on_limit=${does not exist}
        Fail   Should not be executed
    END

On limit message without limit
    [Documentation]     FAIL Error
    WHILE    $variable < 2    on_limit_message=Error
        Log     ${variable}
    END

Wrong WHILE argument
    [Documentation]     FAIL WHILE accepts only one condition, got 3 conditions '$variable < 2', 'limit=5' and 'limit_exceed_messag=Custom error message'.
    WHILE    $variable < 2    limit=5    limit_exceed_messag=Custom error message
        Fail   Should not be executed
    END

On limit message
    [Documentation]     FAIL Custom error message
    WHILE    $variable < 2    limit=${limit}    on_limit_message=Custom error message
        Log     ${variable}
    END

On limit message from variable
    [Documentation]     FAIL ${errorMsg}
    WHILE    $variable < 2    limit=5    on_limit_message=${errorMsg}
        Log     ${variable}
    END

Part of on limit message from variable
    [Documentation]     FAIL While ${errorMsg} 2 ${number}
    WHILE    $variable < 2    limit=5    on_limit_message=While ${errorMsg} 2 ${number}
        Log     ${variable}
    END

No on limit message
    WHILE    $variable < 3    limit=10    on_limit_message=${errorMsg} 2
        Log     ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

Nested while on limit message
    [Documentation]     FAIL ${errorMsg} 2
    WHILE    $variable < 2    limit=5    on_limit_message=${errorMsg} 1
        WHILE    $variable < 2    limit=5    on_limit_message=${errorMsg} 2
            Log     ${variable}
        END
    END

On limit message before limit
    [Documentation]     FAIL Error
    WHILE    $variable < 2    on_limit_message=Error    limit=5
        Log     ${variable}
    END

On limit message with invalid variable
    [Documentation]     FAIL Invalid WHILE loop 'on_limit_message': 'Variable '${nonExisting}' not found.
    WHILE    $variable < 2    on_limit_message=${nonExisting}    limit=5
        Fail   Should not be executed
    END
