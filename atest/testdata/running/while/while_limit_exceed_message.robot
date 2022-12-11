*** Variables ***
${variable}    ${1}
${limit}       11
${number}      ${0.2}
${errorMsg}    Error Message

*** Test Cases ***
limit_exceed_message without limit
    [Documentation]     FAIL Second WHILE loop argument must be 'limit', got 'limit_exceed_message=Error'.
    WHILE    $variable < 2    limit_exceed_message=Error
        Log     ${variable}
    END

Testing error message
    [Documentation]     FAIL Custom error message
    WHILE    $variable < 2    limit=5    limit_exceed_message=Custom error message
        Log     ${variable}
    END

Wrong third argument
    [Documentation]     FAIL Third WHILE loop argument must be 'limit_exceed_message', got 'limit_exceed_messag=Custom error message'.
    WHILE    $variable < 2    limit=5    limit_exceed_messag=Custom error message
        Log     ${variable}
    END

Limit exceed message from variable
    [Documentation]     FAIL ${errorMsg}
    WHILE    $variable < 2    limit=5    limit_exceed_message=${errorMsg}
        Log     ${variable}
    END

Part of limit exceed message from variable
    [Documentation]     FAIL ${errorMsg} 2
    WHILE    $variable < 2    limit=5    limit_exceed_message=${errorMsg} 2
        Log     ${variable}
    END

No error message
    WHILE    $variable < 3    limit=10    limit_exceed_message=${errorMsg} 2
        Log     ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

Nested while error message
    [Documentation]     FAIL ${errorMsg} 2
    WHILE    $variable < 2    limit=5    limit_exceed_message=${errorMsg} 1
        WHILE    $variable < 2    limit=5    limit_exceed_message=${errorMsg} 2
            Log     ${variable}
        END
    END