*** Settings ***
Suite Setup       Without return value
Suite Teardown    Nested keywords with return

*** Test Cases ***

Without return value
    ${ret}=    Without Return Value
    Should Be Equal    ${ret}    ${NONE}
    ${r1}    ${r2}    @{r3}=    Without Return Value
    Should Be Equal    ${r1}    ${NONE}
    Should Be Equal    ${r2}    ${NONE}
    Should Be Empty    ${r3}

With single return value
    ${ret}=    With Single Return Value
    Should Be Equal    ${ret}    something to return

With multiple return values
    ${r1}    ${r2}    ${r3}    ${r4}    ${r5}=     With Multiple Return Values
    Should Be Equal     ${r1}     something
    Should Be Equal     ${r2}     ${True}
    Should Be Equal     ${r3}     ${100}
    Should Be Equal     ${r4}     \\
    Should Be Equal     ${r5}     ${EMPTY}

With variable
    ${ret}=    With variable    foo
    Should Be Equal    ${ret}    foo

With list variable
    ${ret}=    With list variable    1    2    3
    Should Be True    ${ret} == ['0', '1', '2', '3']

Escaping
    ${ret}=    With variable    \${not var}
    Should Be Equal    ${ret}    \${not var}
    ${ret}=    With variable    c:\\temp
    Should Be Equal    ${ret}    c:\\temp

In nested keyword
    ${ret}=    Nested keywords with return
    Should Be Equal    ${ret}    should be returned

Inside for loop in keyword
    ${ret}=    With for loop
    Should Be Equal    ${ret}     return foo

Keyword teardown is run
    ${ret}=    With teardown    ${TEST NAME}
    Should Be Equal    ${ret}     something else to return
    Should Be Equal    ${test var}    ${TEST NAME}

In a keyword inside keyword teardown
    With return in keyword inside teardown

Fails if used directly in keyword teardown
    [Documentation]    FAIL
    ...    Keyword teardown failed:
    ...    Invalid 'RETURN' usage.
    Returning directly from keyword teardown fails
    Fail    Should have failed before this

Fails if used outside keywords
    [Documentation]    FAIL
    ...    Invalid 'RETURN' usage.
    ...
    ...    Also teardown failed:
    ...    Invalid 'RETURN' usage.
    Return From Keyword    ${non existent variable}
    [Teardown]    Return From Keyword

Fails if used outside keywords inside for loop
    [Documentation]    FAIL    Invalid 'RETURN' usage.
    FOR    ${var}    IN    1    2    3
        Return From Keyword
    END

With continuable failure
    [Documentation]    FAIL    continuable error
    ${ret}=    With continuable failure
    Should Be Equal    ${ret}    this should be returned

With continuable failure in for loop
    [Documentation]    FAIL    continuable error
    ${ret}=    With continuable failure in for loop
    Should Be Equal    ${ret}    something to return

Return From Keyword If
    ${ret}=    With Return From Keyword If
    Should Be Equal    ${ret}    something to return

Return From Keyword If does not evaluate bogus arguments if condition is untrue
    [Documentation]    FAIL Replacing variables from keyword return value failed: Variable '\${non existent 2}' not found.
    Return From Keyword If with non-existing variables in arguments

*** Keywords ***
Without Return Value
    Return From Keyword
    Fail    Should have returned before this
    RETURN    Should not ${evaluate}

With Single Return Value
    Return From Keyword    something to return
    Fail    Should have returned before this
    RETURN     Should not ${evaluate}

With Multiple Return Values
    Return From Keyword     something     ${True}     ${100}    \\    ${EMPTY}
    Fail    Should have returned before this
    RETURN     Should    not    ${evaluate}

With variable
    [Arguments]    ${arg}
    Return From Keyword    ${arg}
    Fail     Should have returned before this
    RETURN     Should not ${evaluate}

With list variable
    [Arguments]    @{list}
    Return From Keyword    0    @{list}
    Fail     Should have returned before this
    RETURN     Should not ${evaluate}

Nested keywords with return
    Without Return Value
    ${ret}=    With Single Return Value
    Should Be Equal    ${ret}    something to return
    RETURN    should be returned

With for loop
    FOR    ${var}    IN    foo    bar    baz
           Return From Keyword    return ${var}
           Fail    Should have returned before this
    END
    RETURN     Should not ${evaluate}

With teardown
    [Arguments]    ${arg}
    Return From Keyword    something else to return
    Fail     Should have returned before this
    [Teardown]    Set Test Variable    ${test var}    ${arg}
    RETURN     Should not ${evaluate}

Returning directly from keyword teardown fails
    No Operation
    [Teardown]    Return From Keyword
    RETURN    Should not ${evaluate}

With continuable failure
    Run Keyword And Continue On Failure    Fail    continuable error
    Return From Keyword    this should be returned
    Fail     Should have returned before this
    RETURN     Should not ${evaluate}

With continuable failure in for loop
    FOR    ${var}    IN    foo    bar    baz
           Run Keyword And Continue On Failure    Fail    continuable error
           Return From Keyword    something to return
           Fail    Should have returned before this
    END
    Fail     Should have returned before this
    RETURN     Should not ${evaluate}

With return in keyword inside teardown
    No Operation
    [Teardown]   Without return value

With Return From Keyword If
    Return From Keyword If    ${False}    not returning yet
    Return From Keyword If    1 > 0    something to return
    Fail     Should have returned before this
    RETURN     Should not ${evaluate}

Return From Keyword If with non-existing variables in arguments
    Return From Keyword If    0 > 1    ${non existing 1}
    Return From Keyword If    ${True}    ${non existent 2}
    Fail    Not executed
