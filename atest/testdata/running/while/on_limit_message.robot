*** Variables ***
${variable}    ${1}
${limit}       11
${number}      ${0.2}
${errorMsg}    Error Message

*** Test Cases ***
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


Wrong WHILE arguments
    [Documentation]     FAIL WHILE cannot have more than one condition, got '$variable < 2', 'limite=5' and 'limit_exceed_messag=Custom error message'.
    WHILE    $variable < 2    limite=5    limit_exceed_messag=Custom error message
        Log     ${variable}
    END
