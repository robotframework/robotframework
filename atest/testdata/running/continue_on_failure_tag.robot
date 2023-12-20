*** Settings ***
Library              Exceptions

*** Variables ***
${HEADER}                 Several failures occurred:
${EXC}                    ContinuableApocalypseException

*** Test Cases ***
Continue in test with continue tag
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

Continue in user keyword with continue tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b
    Failure in user keyword with continue tag
    Fail   This should not be executed

Continue in test with continue tag and UK without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw2a\n\n
    ...    2) This should be executed
    [Tags]   robot:CONTINUE-on-failure              # case shouldn't matter
    Failure in user keyword without tag
    Fail   This should be executed

Continue in test with continue tag and nested UK with and without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw2a\n\n
    ...    4) This should be executed
    [Tags]   robot: continue-on-failure             # spaces should be collapsed
    Failure in user keyword with continue tag     run_kw=Failure in user keyword without tag
    Fail   This should be executed

Continue in test with continue tag and two nested UK with continue tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw1a\n\n
    ...    4) kw1b\n\n
    ...    5) This should be executed
    [Tags]   robot:continue-on-failure
    Failure in user keyword with continue tag     run_kw=Failure in user keyword with continue tag
    Fail   This should be executed

Continue in FOR loop with continue tag
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

Continue in FOR loop in UK with continue tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw-loop1-1\n\n
    ...    2) kw-loop1-2\n\n
    ...    3) kw-loop1-3
    FOR loop in in user keyword with continue tag

Continue in FOR loop in UK without tag
    [Documentation]    FAIL kw-loop2-1
    FOR loop in in user keyword without tag

Continue in IF with continue tag
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

Continue in IF in UK with continue tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw7a\n\n
    ...    2) kw7b\n\n
    ...    3) kw7c\n\n
    ...    4) kw7d
    IF in user keyword with continue tag

No continue in IF in UK without tag
    [Documentation]    FAIL kw8a
    IF in user keyword without tag

Continue in Run Keywords with continue tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2
    [Tags]   robot:continue-on-failure
    Run Keywords    Fail   1   AND   Fail   2

Recursive continue in test with continue tag and two nested UK without tag
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

Recursive continue in test with continue tag and two nested UK with and without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b\n\n
    ...    3) kw2a\n\n
    ...    4) kw2b\n\n
    ...    5) This should be executed
    [Tags]   ROBOT:RECURSIVE-CONTINUE-ON-FAILURE        # case shouldn't matter
    Failure in user keyword with continue tag     run_kw=Failure in user keyword without tag
    Fail   This should be executed

Recursive continue in test with continue tag and UK with stop tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw4a\n\n
    ...    2) This should be executed
    [Tags]   robot:recursive-continue-on-failure
    Failure in user keyword with stop tag
    Fail   This should be executed

Recursive continue in test with continue tag and UK with recursive stop tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw11a\n\n
    ...    2) This should be executed
    [Tags]   robot:recursive-continue-on-failure
    Failure in user keyword with recursive stop tag
    Fail   This should be executed

Recursive continue in user keyword
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw3a\n\n
    ...    2) kw3b\n\n
    ...    3) kw2a\n\n
    ...    4) kw2b
    Failure in user keyword with recursive continue tag     run_kw=Failure in user keyword without tag
    Fail   This should not be executed

Recursive continue in nested keyword
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw3a\n\n
    ...    2) kw3b
    Failure in user keyword without tag     run_kw=Failure in user keyword with recursive continue tag
    Fail   This should not be executed

stop-on-failure in keyword in Teardown
    [Documentation]    FAIL    Teardown failed:\nkw4a
    [Teardown]   Failure in user keyword with stop tag
    No Operation

stop-on-failure with continuable failure in keyword in Teardown
    [Documentation]     FAIL    Teardown failed:\n${HEADER}\n\n
    ...    1) ${EXC}: kw9a\n\n
    ...    2) kw9b
    [Teardown]   Continuable Failure in user keyword with stop tag
    No Operation

stop-on-failure with run-kw-and-continue failure in keyword in Teardown
    [Documentation]     FAIL    Teardown failed:\n${HEADER}\n\n
    ...    1) kw10a\n\n
    ...    2) kw10b
    [Teardown]   run-kw-and-continue failure in user keyword with stop tag
    No Operation

stop-on-failure with run-kw-and-continue failure in keyword
    [Documentation]     FAIL    ${HEADER}\n\n
    ...    1) kw10a\n\n
    ...    2) kw10b
    run-kw-and-continue failure in user keyword with stop tag

Test teardown using run keywords with stop tag in test case
    [Documentation]    FAIL    Teardown failed:\n1
    [Tags]   robot:stop-on-failure
    [Teardown]   Run Keywords    Fail    1    AND    Fail    2
    No Operation

Test teardown using user keyword with stop tag in test case
    [Documentation]    FAIL    Teardown failed:\n${HEADER}\n\n
    ...    1) kw2a\n\n
    ...    2) kw2b
    [Tags]   robot:stop-on-failure
    [Teardown]    Failure in user keyword without tag
    No Operation

Test teardown using user keyword with recursive stop tag in test case
    [Documentation]    FAIL    Teardown failed:\nkw2a
    [Tags]   robot:recursive-stop-on-failure
    [Teardown]    Failure in user keyword without tag
    No Operation

Test Teardown with stop tag in user keyword
    [Documentation]    FAIL    Keyword teardown failed:\nkw5a
    Teardown with stop tag in user keyword
    No Operation

Test Teardown with recursive stop tag in user keyword
    [Documentation]    FAIL    Keyword teardown failed:\nkw6a
    Teardown with recursive stop tag in user keyword

Test Teardown with recursive stop tag and UK with continue tag
    # continue-on-failure overrides recursive-stop-on-failure
    [Documentation]    FAIL    Keyword teardown failed:\n${HEADER}\n\n
    ...    1) kw1a\n\n
    ...    2) kw1b
    Teardown with recursive stop tag in user keyword    run_kw=Failure in user keyword with continue tag

Test Teardown with recursive stop tag and UK with recursive continue tag
    # recursive-continue-on-failure overrides recursive-stop-on-failure
    [Documentation]    FAIL    Keyword teardown failed:\n${HEADER}\n\n
    ...    1) kw3a\n\n
    ...    2) kw3b
    Teardown with recursive stop tag in user keyword    run_kw=Failure in user keyword with recursive continue tag

stop-on-failure with Template
    [Documentation]    FAIL    42 != 43
    [Tags]   robot:stop-on-failure
    [Template]    Should Be Equal
    Same         Same
    42           43
    Something    Different

recursive-stop-on-failure with Template
    [Documentation]    FAIL    42 != 43
    [Tags]   robot:recursive-stop-on-failure
    [Template]    Should Be Equal
    Same         Same
    42           43
    Something    Different

stop-on-failure with Template and Teardown
    [Documentation]    FAIL    42 != 43\n\nAlso teardown failed:\n1
    [Tags]   robot:stop-on-failure
    [Teardown]   Run Keywords   Fail   1   AND   Fail  2
    [Template]    Should Be Equal
    Same         Same
    42           43
    Something    Different

stop-on-failure does not stop continuable failure in test
    [Documentation]     FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2
    [Tags]   robot:stop-on-failure
    Run Keyword And Continue On Failure    Fail    1
    Fail    2

Test recursive-continue-recursive-stop
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw11a\n\n
    ...    2) 2
    [Tags]    robot:recursive-continue-on-failure
    Failure in user keyword with recursive stop tag
    Fail    2

Test recursive-stop-recursive-continue
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw3a\n\n
    ...    2) kw3b
    [Tags]    robot:recursive-stop-on-failure
    Failure in user keyword with recursive continue tag
    Fail    2

Test recursive-stop-recursive-continue-recursive-stop
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) kw3a\n\n
    ...    2) kw3b\n\n
    ...    3) kw11a
    [Tags]    robot:recursive-stop-on-failure
    Failure in user keyword with recursive continue tag    run_kw=Failure in user keyword with recursive stop tag
    Fail    2

Test test setup with continue-on-failure
    [Documentation]    FAIL Setup failed:\n
    ...    setup-1
    [Tags]      robot:continue-on-failure
    [Setup]     test setup
    Fail    should-not-run

Test test setup with recursive-continue-on-failure
    [Documentation]    FAIL Setup failed:\n${HEADER}\n\n
    ...    1) setup-1\n\n
    ...    2) setup-2
    [Tags]      robot:recursive-continue-on-failure
    [Setup]     test setup
    Fail    should-not-run

recursive-stop-on-failure with continue-on-failure
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 1.1.1
    ...
    ...    2) 2.1.1
    ...
    ...    3) 3.1.1
    ...
    ...    4) t1.1.1
    ...
    ...    5) t2.1.1
    ...
    ...    Also teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) 1.1.1
    ...
    ...    2) 2.1.1
    ...
    ...    3) 3.1.1
    [Tags]    robot:recursive-stop-on-failure    robot:continue-on-failure
    recursive-stop-on-failure with continue-on-failure
    Step t1
    Step t2
    [Teardown]    recursive-stop-on-failure with continue-on-failure

recursive-continue-on-failure with stop-on-failure
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 1.1.1
    ...
    ...    2) 1.1.2
    ...
    ...    3) 1.2.1
    ...
    ...    4) 1.2.2
    ...
    ...    Also teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) 1.1.1
    ...
    ...    2) 1.1.2
    ...
    ...    3) 1.2.1
    ...
    ...    4) 1.2.2
    [Tags]    robot:recursive-continue-on-failure    robot:stop-on-failure
    recursive-continue-on-failure with stop-on-failure
    Step t1
    Step t2
    [Teardown]    recursive-continue-on-failure with stop-on-failure

*** Keywords ***
Failure in user keyword with continue tag
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

Failure in user keyword with recursive continue tag
    [Arguments]    ${run_kw}=No Operation
    [Tags]   robot:recursive-continue-on-failure
    Fail   kw3a
    Fail   kw3b
    Log    This should be executed
    Run Keyword   ${run_kw}

Failure in user keyword with stop tag
    [Tags]   robot:stop-on-failure
    Fail   kw4a
    Log    This should not be executed
    Fail   kw4b

Failure in user keyword with recursive stop tag
    [Tags]    robot:recursive-stop-on-failure
    Fail    kw11a
    Log     This is not executed
    Fail    kw11b

Teardown with stop tag in user keyword
    [Tags]   robot:stop-on-failure
    [Teardown]   Run Keywords    Fail  kw5a   AND   Fail   kw5b
    No Operation

Teardown with recursive stop tag in user keyword
    [Arguments]    ${run_kw}=No Operation
    [Tags]   robot:recursive-stop-on-failure
    [Teardown]   Run Keywords    ${run_kw}   AND   Fail  kw6a   AND   Fail   kw6b
    No Operation

FOR loop in in user keyword with continue tag
    [Tags]   robot:continue-on-failure
    FOR    ${val}    IN    1    2    3
        Fail   kw-loop1-${val}
    END

FOR loop in in user keyword without tag
    FOR    ${val}    IN    1    2    3
        Fail   kw-loop2-${val}
    END

IF in user keyword with continue tag
    [Tags]   robot:continue-on-failure
    IF   1==1
        Fail    kw7a
        Fail    kw7b
    END
    IF   1==2
        No Operation
    ELSE
        Fail    kw7c
        Fail    kw7d
    END

IF in user keyword without tag
    IF   1==1
        Fail    kw8a
        Fail    kw8b
    END
    IF   1==2
        No Operation
    ELSE
        Fail    kw8c
        Fail    kw8d
    END

Continuable Failure in user keyword with stop tag
    [Tags]   robot:stop-on-failure
    Raise Continuable Failure    kw9a
    Log    This is executed
    Fail    kw9b
    Log    This is not executed
    Fail    kw9c

run-kw-and-continue failure in user keyword with stop tag
    [Tags]   robot:stop-on-failure
    Run Keyword And Continue On Failure    Fail    kw10a
    Log    This is executed
    Fail    kw10b
    Log    This is not executed
    Fail    kw10c

test setup
    Fail    setup-1
    Fail    setup-2

recursive-stop-on-failure with continue-on-failure
    [Tags]    robot:recursive-stop-on-failure    robot:continue-on-failure
    Step 1
    Step 2
    Step 3

recursive-continue-on-failure with stop-on-failure
    [Tags]    robot:recursive-continue-on-failure    robot:stop-on-failure
    Step 1
    Step 2
    Step 3

Step ${x}
    Step ${x}.1
    Step ${x}.2

Step ${x}.${y}
    Fail    ${x}.${y}.1
    Fail    ${x}.${y}.2
