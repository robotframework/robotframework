*** Settings ***
Suite Teardown    Recursion With Run Keyword

*** Variables ***
${PTD FAILED}        \n\nAlso parent suite teardown failed:\nMaximum limit of started keywords exceeded.
${LIMIT EXCEEDED}    Maximum limit of started keywords exceeded.${PTD FAILED}


*** Test Cases ***

Infinite recursion
    [Documentation]    FAIL ${LIMIT EXCEEDED}
    Recursion

Infinite cyclic recursion
    [Documentation]    FAIL ${LIMIT EXCEEDED}
    Cyclic recursion

Infinite recursion with Run Keyword
    [Documentation]    FAIL ${LIMIT EXCEEDED}
    Recursion with Run Keyword

Infinitely recursive for loop
    [Documentation]    FAIL ${LIMIT EXCEEDED}
    Infinitely recursive for loop

Recursion below the recursion limit is ok
    [Documentation]    FAIL Still below limit!${PTD FAILED}
    Limited recursion
    Recursive for loop    10
    Failing limited recursion

*** Keywords ***
Recursion
    Recursion

Limited recursion
    [Arguments]    ${limit}=${15}
    Run Keyword If    ${limit} > 0    Limited recursion   ${limit - 1}

Failing limited recursion
    [Arguments]    ${limit}=${30}
    Run Keyword If    ${limit} < 0    Fail    Still below limit!
    Failing limited recursion     ${limit - 1}

Cyclic recursion
    Cyclic recursion 2

Cyclic recursion 2
    Cyclic recursion 3

Cyclic recursion 3
    Cyclic recursion

Recursion With Run Keyword
    Run Keyword    Recursion With Run Keyword

Recursive for loop
    [Arguments]    ${rounds}
    FOR    ${i}    IN RANGE    ${rounds}
        Recursive for loop    ${i}
    END

Infinitely recursive for loop
    FOR    ${var}    IN    recursion
        Infinitely recursive for loop
    END
