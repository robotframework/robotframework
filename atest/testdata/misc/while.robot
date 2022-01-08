*** Test cases ***
While loop executed multiple times
    ${variable}=     Set variable     ${1}
    WHILE    $variable < 6
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
    END

While loop in keyword
    While loop executed multiple times

*** Keywords ***
While loop executed multiple times
    ${variable}=     Set variable     ${1}
    WHILE    $variable < 6
        Log    ${variable}
        ${variable}=    Evaluate    $variable + 1
    END
