*** Variables ***
${variable}    ${1}
${limit}       11
${number}      ${0.2}

*** Test Cases ***
Default limit is 10000 iterations
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 10000 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2
        Log    ${variable}
    END

Limit with iteration count
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 5 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=5
        Log    ${variable}
    END

Limit with iteration count with spaces
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 30 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=3 0
        Log    ${variable}
    END

Limit with iteration count with underscore
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 10 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=1_0
        Log    ${variable}
    END

Limit as timestr
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 0.1 seconds. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=0.1s
        Log     ${variable}
    END

Limit from variable
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 11 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=${limit}
        Log     ${variable}
    END

Part of limit from variable
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 0.2 seconds. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=${number} s
        Log     ${variable}
    END

Limit can be disabled
    WHILE    $variable < 110    limit=NoNe
        Log     ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

No condition with limit
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 2 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    limit=2
        Log    Hello
    END

Invalid limit invalid suffix
    [Documentation]     FAIL Invalid WHILE loop limit: Invalid time string '1 times'.
    WHILE    $variable < 2    limit=1 times
        Log     ${variable}
    END

Invalid limit invalid value
    [Documentation]     FAIL Invalid WHILE loop limit: Iteration count must be a positive integer, got '-100'.
    WHILE    $variable < 2    limit=-100
        Log     ${variable}
    END

Invalid limit mistyped prefix
    [Documentation]     FAIL WHILE cannot have more than one condition, got '$variable < 2' and 'limitation=-1x'.
    WHILE    $variable < 2    limitation=-1x
        Log     ${variable}
    END

Invalid values after limit
    [Documentation]     FAIL WHILE cannot have more than one condition, got '$variable < 2', 'limit=-1x', 'invalid' and 'values'.
    WHILE    $variable < 2    limit=-1x    invalid    values
        Log     ${variable}
    END
