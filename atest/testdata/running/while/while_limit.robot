*** Variables ***
${variable}    ${1}
${limit}       11 x
${number}      ${8}

*** Test Cases ***
Default limit is 100 iterations
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 100 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2
        Log    ${variable}
    END

Limit with x iterations
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 5 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=5x
        Log    ${variable}
    END

Limit with times iterations
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 3 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=3 times
        Log    ${variable}
    END

Limit as timestr
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 0.5 seconds. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=0.5s
        Log     ${variable}
    END

Limit from variable
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 11 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=${limit}
        Log     ${variable}
    END

Part of limit from variable
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 8 iterations. Use the 'limit' argument to increase or remove the limit if needed.
    WHILE    $variable < 2    limit=${number} times
        Log     ${variable}
    END

Limit can be disabled
    WHILE    $variable < 110    limit=NoNe
        Log     ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

Invalid limit no suffix
    [Documentation]     FAIL Invalid WHILE loop limit: Invalid time string '1'.
    WHILE    $variable < 2    limit=1
        Log     ${variable}
    END

Invalid limit invalid value
    [Documentation]     FAIL Invalid WHILE loop limit: Iteration limit must be positive integer when using 'x' or 'times', got: 'fdas '
    WHILE    $variable < 2    limit=fdas x
        Log     ${variable}
    END

Invalid negative limit
    [Documentation]     FAIL Invalid WHILE loop limit: Iteration limit must be positive integer when using 'x' or 'times', got: '-1'
    WHILE    $variable < 2    limit=-1x
        Log     ${variable}
    END

Invalid limit mistyped prefix
    [Documentation]     FAIL Second WHILE loop argument must be 'limit', got limitation=-1x.
    WHILE    $variable < 2    limitation=-1x
        Log     ${variable}
    END

Invalid values after limit
    [Documentation]     FAIL WHILE cannot have more than one condition.
    WHILE    $variable < 2    limit=-1x    invalid    values
        Log     ${variable}
    END
