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

Continue in test with Set Tags
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2
    Set Tags   ROBOT:CONTINUE-ON-FAILURE            # case shouldn't matter
    Fail   1
    Fail   2
    Log    This should be executed

Continue in user keyword with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b
    Failure in user keyword with tag
    Fail   This should not be executed

Continue in test with tag and UK without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw2a\n\n
    ...    2) This should be executed
    [Tags]   robot:CONTINUE-on-failure              # case shouldn't matter
    Failure in user keyword without tag
    Fail   This should be executed

Continue in test with tag and nested UK with and without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw2a\n\n
    ...    4) This should be executed
    [Tags]   robot: continue-on-failure             # spaces should be collapsed
    Failure in user keyword with tag     run_kw=Failure in user keyword without tag
    Fail   This should be executed

Continue in test with tag and two nested UK with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw1a\n\n
    ...    4) kw1b\n\n
    ...    5) This should be executed
    [Tags]   robot:continue-on-failure
    Failure in user keyword with tag     run_kw=Failure in user keyword with tag
    Fail   This should be executed

Continue in FOR loop with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) loop-1\n\n
    ...    2) loop-2\n\n
    ...    3) loop-3
    [Tags]   robot:continue-on-failure
    FOR    ${val}    IN    1    2    3
        Fail   loop-${val}
    END

Continue in FOR loop with Set Tags
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) loop-1\n\n
    ...    2) loop-2\n\n
    ...    3) loop-3
    FOR    ${val}    IN    1    2    3
        Set Tags   robot:continue-on-failure
        Fail   loop-${val}
    END

No continue in FOR loop without tag
    [Documentation]    FAIL loop-1
    FOR    ${val}    IN    1    2    3
        Fail   loop-${val}
    END

Continue in FOR loop in UK with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw-loop-1\n\n
    ...    2) kw-loop-2\n\n
    ...    3) kw-loop-3
    FOR loop in in user keyword with tag

Continue in FOR loop in UK without tag
    [Documentation]    FAIL kw-loop-1
    FOR loop in in user keyword without tag

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

Continue in IF with set and remove tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2\n\n
    ...    3) 3
    Set Tags   robot:continue-on-failure
    IF   1==1
        Fail    1
        Fail    2
    END
    Remove Tags   robot:continue-on-failure
    IF   1==2
        No Operation
    ELSE
        Fail    3
        Fail    this is not executed
    END

No continue in IF without tag
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
    IF in user keyword with tag

No continue in IF in UK without tag
    [Documentation]    FAIL kw1a
    IF in user keyword without tag

Continue in Run Keywords with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2
    [Tags]   robot:continue-on-failure
    Run Keywords    Fail   1   AND   Fail   2

Recursive continue in test with tag and two nested UK without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw2a\n\n
    ...    2) kw2b\n\n
    ...    3) kw2a\n\n
    ...    4) kw2b\n\n
    ...    5) This should be executed
    [Tags]   robot:recursive-continue-on-failure
    Failure in user keyword without tag     run_kw=Failure in user keyword without tag
    Fail   This should be executed

Recursive continue in test with Set Tags and two nested UK without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw2a\n\n
    ...    2) kw2b\n\n
    ...    3) kw2a\n\n
    ...    4) kw2b\n\n
    ...    5) This should be executed
    Set Tags   robot: recursive-continue-on-failure     # spaces should be collapsed
    Failure in user keyword without tag     run_kw=Failure in user keyword without tag
    Fail   This should be executed

Recursive continue in test with tag and two nested UK with and without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw2a\n\n
    ...    4) kw2b\n\n
    ...    5) This should be executed
    [Tags]   ROBOT:RECURSIVE-CONTINUE-ON-FAILURE        # case shouldn't matter
    Failure in user keyword with tag     run_kw=Failure in user keyword without tag
    Fail   This should be executed

Recursive continue in user keyword
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw2a\n\n
    ...    4) kw2b
    Failure in user keyword with recursive tag     run_kw=Failure in user keyword without tag
    Fail   This should not be executed

Recursive continue in nested keyword
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b
    Failure in user keyword without tag     run_kw=Failure in user keyword with recursive tag
    Fail   This should not be executed

*** Keywords ***
Failure in user keyword with tag
    [Arguments]    ${run_kw}=No Operation
    [Tags]   robot:continue-on-failure
    Fail   kw1a
    Fail   kw1b
    Log    This should be executed
    Run Keyword   ${run_kw}

Failure in user keyword without tag
    [Arguments]    ${run_kw}=No Operation
    Run Keyword   ${run_kw}
    Fail   kw2a
    Fail   kw2b

Failure in user keyword with recursive tag
    [Arguments]    ${run_kw}=No Operation
    [Tags]   robot:recursive-continue-on-failure
    Fail   kw1a
    Fail   kw1b
    Log    This should be executed
    Run Keyword   ${run_kw}

FOR loop in in user keyword with tag
    [Tags]   robot:continue-on-failure
    FOR    ${val}    IN    1    2    3
        Fail   kw-loop-${val}
    END

FOR loop in in user keyword without tag
    FOR    ${val}    IN    1    2    3
        Fail   kw-loop-${val}
    END

IF in user keyword with tag
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

IF in user keyword without tag
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
