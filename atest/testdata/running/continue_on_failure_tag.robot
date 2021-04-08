*** Settings ***
Library              Exceptions

*** Variables ***
${HEADER}                 Several failures occurred:

*** Test Cases ***
Continue in test with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2
    [Tags]   robot:continue-on-failure
    Fail   1
    Fail   2
    Log    This should be executed

Continue in test with negative tag 
    [Documentation]    FAIL 1
    [Tags]   robot:no-continue-on-failure
    Fail   1
    Fail   2

Continue in test with negative tag and continuable error
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) ContinuableApocalypseException: 1\n\n
    ...    2) 2\n\n
    ...    3) 3
    [Tags]   robot:no-continue-on-failure
    # continuable keywords should still be able to continue
    # even when robot:no-continue-on-failure is set.
    Raise Continuable Failure   1
    Run Keyword and Continue on Failure   Fail  2
    Fail   3
    Fail   4

Continue in user kewyord with tag
    [Documentation]    FAIL kw1
    Failure in user keyword using tag and run keyword "No Operation"

# test shows that user-kw tags aren't propogated down. 
# if it was propagated, we would also see kw3b failure
Continue in nested user kewyord with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1\n\n
    ...    2) kw3a
    Failure in user keyword using tag and run keyword "Failure in user keyword without tag"

Continue in test with tag and user-kw without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw2a\n\n
    ...    2) kw2b
    [Tags]   robot:continue-on-failure
    Failure in user keyword without tag and run keyword "No Operation"
    Log    This should be executed

Continue in test with tag and nested UK with and without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw2a\n\n
    ...    2) kw2b\n\n
    ...    3) kw4a
    [Tags]   robot:continue-on-failure
    Failure in user keyword without tag and run keyword "Failure in user keyword with negative tag"
    Log    This should be executed

Continue in for loop with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) loop-1\n\n
    ...    2) loop-2\n\n
    ...    3) loop-3
    [Tags]   robot:continue-on-failure
    FOR    ${val}    IN    1    2    3
        Fail   loop-${val}
    END

Continue in for loop without tag
    [Documentation]    FAIL loop-1
    FOR    ${val}    IN    1    2    3
        Fail   loop-${val}
    END

Continue in for loop in UK with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw-loop-1\n\n
    ...    2) kw-loop-2\n\n
    ...    3) kw-loop-3
    [Tags]   robot:continue-on-failure
    For Loop in in user keyword

Continue in for loop in UK without tag
    [Documentation]    FAIL kw-loop-1
    For Loop in in user keyword

*** Keywords ***

Failure in user keyword using tag and run keyword "${kw}"
    [Tags]   robot:continue-on-failure
    Fail   kw1
    Log    This should be executed
    Run Keyword   ${kw}

Failure in user keyword without tag and run keyword "${kw}"
    Fail   kw2a
    Fail   kw2b
    Log    Continued on failure
    Run Keyword   ${kw}

Failure in user keyword without tag
    Fail   kw3a
    Fail   kw3b
    Log    Continued on failure

Failure in user keyword with negative tag
    [Tags]   robot:no-continue-on-failure
    Fail   kw4a
    Log    This should not be executed
    Fail   kw4b

For Loop in in user keyword
    FOR    ${val}    IN    1    2    3
        Fail   kw-loop-${val}
    END
