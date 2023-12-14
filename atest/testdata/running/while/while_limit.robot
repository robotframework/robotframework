*** Variables ***
${variable}    ${1}
${limit}       11
${number}      ${0.2}
${USE LIMIT}   Use the 'limit' argument to increase or remove the limit if needed.

*** Test Cases ***
Default limit is 10000 iterations
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 10000 iterations. ${USE LIMIT}
    WHILE    $variable < 2
        Log    ${variable}
    END

Limit with iteration count
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 5 iterations. ${USE LIMIT}
    WHILE    $variable < 2    limit=5
        Log    ${variable}
    END

Iteration count with 'times' suffix
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 3 iterations. ${USE LIMIT}
    WHILE    $variable < 2    limit=3 times
        Log    ${variable}
    END

Iteration count with 'x' suffix
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 4 iterations. ${USE LIMIT}
    WHILE    $variable < 2    limit=4x
        Log    ${variable}
    END

Iteration count normalization
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 30 iterations. ${USE LIMIT}
    WHILE    limit=1_000
        BREAK
    END
    WHILE    $variable < 2    limit=3 0 T i m e S
        Log    ${variable}
    END

Limit as timestr
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 100 milliseconds. ${USE LIMIT}
    WHILE    $variable < 2    limit=0.1s
        Log     ${variable}
    END

Limit from variable
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 11 iterations. ${USE LIMIT}
    WHILE    $variable < 2    limit=${limit}
        Log     ${variable}
    END

Part of limit from variable
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 200 milliseconds. ${USE LIMIT}
    WHILE    $variable < 2    limit=${number} s
        Log     ${variable}
    END

Limit can be disabled
    WHILE    $variable < 110    limit=NoNe
        Log     ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

No condition with limit
    [Documentation]     FAIL WHILE loop was aborted because it did not finish within the limit of 2 iterations. ${USE LIMIT}
    WHILE    limit=2
        Log    Hello
    END

Limit exceeds in teardown
    [Documentation]    FAIL
    ...    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) WHILE loop was aborted because it did not finish within the limit of 42 milliseconds. ${USE LIMIT}
    ...
    ...    2) Failing after WHILE
    No Operation
    [Teardown]    Limit exceeds

Limit exceeds after failures in teardown
    [Documentation]    FAIL
    ...    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Hello!
    ...
    ...    2) Hello!
    ...
    ...    3) WHILE loop was aborted because it did not finish within the limit of 2 iterations. ${USE LIMIT}
    No Operation
    [Teardown]    Limit exceeds after failures

Continue after limit in teardown
    No Operation
    [Teardown]    Continue after limit

Invalid limit invalid suffix
    [Documentation]     FAIL Invalid WHILE loop limit: Invalid time string '1 bad'.
    WHILE    $variable < 2    limit=1 bad
        Fail    Should not be executed
    END

Invalid limit invalid value
    [Documentation]     FAIL Invalid WHILE loop limit: Iteration count must be a positive integer, got '-100'.
    WHILE    $variable < 2    limit=-100
        Fail    Should not be executed
    END

Invalid limit mistyped prefix
    [Documentation]     FAIL WHILE accepts only one condition, got 2 conditions '$variable < 2' and 'limitation=2'.
    WHILE    $variable < 2    limitation=2
        Fail    Should not be executed
    END

Limit used multiple times
    [Documentation]     FAIL WHILE accepts only one condition, got 2 conditions 'True' and 'limit=1'.
    WHILE    True    limit=1    limit=2
        Fail    Should not be executed
    END

Invalid values after limit
    [Documentation]     FAIL WHILE accepts only one condition, got 3 conditions '$variable < 2', 'limit=2' and 'invalid'.
    WHILE    $variable < 2    limit=2    invalid
        Fail    Should not be executed
    END

*** Keywords ***
Limit exceeds
    WHILE    limit=0.042s
        Log    Hello!
    END
    Fail    Failing after WHILE

Limit exceeds after failures
    WHILE    limit=2
        Fail    Hello!
    END

Continue after limit
    WHILE    limit=0.042s    on_limit=pass
        Log    Hello!
    END
