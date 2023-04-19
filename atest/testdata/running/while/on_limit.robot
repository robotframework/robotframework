*** Variables ***
${variable}    ${1}
${limit}       11
${number}      ${0.2}
${pass}        Pass
${errorMsg}    Error Message

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
    [Documentation]    FAIL WHILE loop was aborted because it did not finish within the limit of 5 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    True    limit=5    on_limit=FaIl
        No Operation
    END

On limit pass with failures in loop
    [Documentation]    FAIL Oh no!
    WHILE    True    limit=5    on_limit=pass
        Fail   Oh no!
    END

On limit pass with continuable failure
    [Documentation]    FAIL Third failure, this time a hard one.
    WHILE    limit=2    on_limit=pass
        Run Keyword And Continue On Failure    Fail    Continuable failure!
    END
    Fail    Third failure, this time a hard one.

On limit fail with continuable failure
    [Documentation]    FAIL Several failures occurred:\n\n
    ...   1) Continuable failure!\n\n
    ...   2) Continuable failure!\n\n
    ...   3) WHILE loop was aborted because it did not finish within the limit of 2 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    limit=2    on_limit=fail
        Run Keyword And Continue On Failure    Fail    Continuable failure!
    END
    Fail    Should not be executed!

Invalid on_limit
    [Documentation]    FAIL Invalid WHILE loop 'on_limit' value 'inValid': Value must be 'PASS' or 'FAIL'.
    WHILE    True    limit=5    on_limit=inValid
        Fail   Oh no!
    END

On limit without limit defined
    [Documentation]    FAIL WHILE on_limit option cannot be used without limit.
    WHILE    True    on_limit=PaSS
        No Operation
    END

On limit with invalid variable
    [Documentation]    FAIL Invalid WHILE loop 'on_limit' value '${does not exist}': Variable '${does not exist}' not found.
    WHILE    True    limit=5    on_limit=${does not exist}
        Fail   Oh no!
    END

On limit message without limit
    [Documentation]     FAIL Error
    WHILE    $variable < 2    on_limit_message=Error
        Log     ${variable}
    END

Wrong WHILE argument
    [Documentation]     FAIL WHILE cannot have more than one condition, got '$variable < 2', 'limit=5' and 'limit_exceed_messag=Custom error message'.
    WHILE    $variable < 2    limit=5    limit_exceed_messag=Custom error message
        Log     ${variable}
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

On limit messge with invalid variable
    [Documentation]     FAIL Invalid WHILE loop 'on_limit_message': 'Variable '${nonExisting}' not found.
    WHILE    $variable < 2    on_limit_message=${nonExisting}    limit=5
        Log     ${variable}
    END


Wrong WHILE arguments
    [Documentation]     FAIL WHILE cannot have more than one condition, got '$variable < 2', 'limite=5' and 'limit_exceed_messag=Custom error message'.
    WHILE    $variable < 2    limite=5    limit_exceed_messag=Custom error message
        Log     ${variable}
    END
