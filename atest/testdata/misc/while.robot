*** Test cases ***
WHILE loop executed multiple times
    ${variable}=     Set variable     ${1}
    WHILE    $variable < 6
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

WHILE loop in keyword
    WHILE loop executed multiple times

*** Keywords ***
WHILE loop executed multiple times
    ${variable}=     Set variable     ${1}
    WHILE    True
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
        IF    $variable == 5    CONTINUE
        IF    $variable == 6    BREAK
    END
