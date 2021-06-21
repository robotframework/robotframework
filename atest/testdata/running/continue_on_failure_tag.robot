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

Continue in user kewyord with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b
    Failure in user keyword using tag
    Fail   This should not be executed

Continue in test with tag and UK without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw2a\n\n
    ...    2) This should be executed
    [Tags]   robot:continue-on-failure
    Failure in user keyword without tag
    Fail   This should be executed

Continue in test with tag and nested UK with and without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw2a\n\n
    ...    4) This should be executed
    [Tags]   robot:continue-on-failure
    Failure in user keyword using tag     run_kw=Failure in user keyword without tag
    Fail   This should be executed

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
    For Loop in in user keyword with tag

Continue in for loop in UK without tag
    [Documentation]    FAIL kw-loop-1
    For Loop in in user keyword without tag

Continue in IF with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2\n\n
    ...    3) 3\n\n
    ...    4) 4

    [Tags]   robot:continue-on-failure
    IF   1==1
        Fail    1
        Fail    2
    END
    IF   1==2
        No Operation
    ELSE
        Fail    3
        Fail    4
    END

Continue in IF without tag
    [Documentation]    FAIL 1
    IF   1==1
        Fail    1
        Fail    This should not be executed
    END

Continue in IF in UK with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw1c\n\n
    ...    4) kw1d
    If in user keyword with tag

Continue in IF in UK without tag
    [Documentation]    FAIL kw1a
    If in user keyword without tag


*** Keywords ***

Failure in user keyword using tag
    [Tags]   robot:continue-on-failure
    [Arguments]    ${run_kw}=No Operation
    Fail   kw1a
    Fail   kw1b
    Log    This should be executed
    Run Keyword   ${run_kw}

Failure in user keyword without tag
    Fail   kw2a
    Fail   kw2b

For Loop in in user keyword with tag
    [Tags]   robot:continue-on-failure
    FOR    ${val}    IN    1    2    3
        Fail   kw-loop-${val}
    END

For Loop in in user keyword without tag
    FOR    ${val}    IN    1    2    3
        Fail   kw-loop-${val}
    END

If in user keyword with tag
    [Tags]   robot:continue-on-failure
    IF   1==1
        Fail    kw1a
        Fail    kw1b
    END
    IF   1==2
        No Operation
    ELSE
        Fail    kw1c
        Fail    kw1d
    END

If in user keyword without tag
    IF   1==1
        Fail    kw1a
        Fail    kw1b
    END
    IF   1==2
        No Operation
    ELSE
        Fail    kw1c
        Fail    kw1d
    END
