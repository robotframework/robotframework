*** Settings ***
Suite Setup       Run some while
Suite Teardown    Run some while


*** Test Cases ***
Inside FOR
    FOR   ${i}    IN RANGE    3
        WHILE    $i < 4
            Log    {i}
            ${i}=     Evaluate    $i + 1
        END
    END

Failing inside FOR
    [Documentation]    FAIL 0 != 1
    FOR   ${i}    IN RANGE    3
        WHILE    $i < 4
            Should be equal     ${0}     ${i}
            ${i}=     Evaluate    $i + 1
        END
    END

Inside IF
    IF    True
        ${i}=    Set variable     ${0}
        WHILE    $i < 4
            Log    {i}
            ${i}=     Evaluate    $i + 1
        END
    END


*** Keywords ***
Run some while
    ${i}=    Set variable     ${0}
    WHILE    $i < 4
        Log    {i}
        ${i}=     Evaluate    $i + 1
    END
