*** Settings ***
Suite Teardown       Continuable Failure In User Keyword In Suite Teardown
Library              Exceptions

*** Variables ***
${HEADER}                 Several failures occurred:
${EXC}                    ContinuableApocalypseException
${ERROR}                  ${EXC}: Can be continued
${TEARDOWN ERROR}         Also parent suite teardown failed:\nContinuableApocalypseException: Can be continued
${ERROR WITH TEARDOWN}    ${ERROR}\n\n${TEARDOWN ERROR}

*** Test Cases ***
Continue in test
    [Documentation]    FAIL ${ERROR WITH TEARDOWN}
    Raise Continuable Failure
    Log    This should be executed

Continue in user keyword
    [Documentation]    FAIL ${ERROR WITH TEARDOWN}
    Continuable Failure In User Keyword In Test Case

Continue in test with several continuable failures
    [Documentation]     FAIL ${HEADER}\n\n
    ...    1) ${EXC}: A\n\n
    ...    2) ${EXC}: B\n\n
    ...    3) ${EXC}: C\n\n
    ...    ${TEARDOWN ERROR}
    Raise Continuable Failure    A
    Log    This should be executed
    Raise Continuable Failure    B
    Log    This should also be executed
    Raise Continuable Failure    C
    Log    This too should also be executed

Continue in user keyword with several continuable failures
    [Documentation]     FAIL ${HEADER}\n\n
    ...    1) ${EXC}: 1\n\n
    ...    2) ${EXC}: 2\n\n
    ...    3) ${EXC}: 3\n\n
    ...    4) ${EXC}: 1\n\n
    ...    5) ${EXC}: 2\n\n
    ...    6) ${EXC}: 3\n\n
    ...    ${TEARDOWN ERROR}
    Several Continuable Failures In User Keyword In Test Case
    Several Continuable Failures In User Keyword In Test Case, Again

Continuable and regular failure
    [Documentation]     FAIL ${HEADER}\n\n
    ...    1) ${ERROR}\n\n
    ...    2) Stopping here!! (with ∏ön ÄßÇïï €§)\n\n
    ...    ${TEARDOWN ERROR}
    Raise Continuable Failure
    Log    This should be executed
    Fail    Stopping here!! (with ∏ön ÄßÇïï €§)
    Fail    This should not be executed

Continue in nested user keyword
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) ${ERROR} in top level (with ∏ön ÄßÇïï €§)\n\n
    ...    2) ${EXC}: 1\n\n
    ...    3) ${EXC}: 2\n\n
    ...    4) ${EXC}: 3\n\n
    ...    5) ${ERROR} in top level after nesting (with ∏ön ÄßÇïï €§)\n\n
    ...    ${TEARDOWN ERROR}
    Continuable Failure In Nested UK

Continuable and regular failure in UK
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) ${EXC}: one\n\n
    ...    2) ${EXC}: two\n\n
    ...    3) Stop!!\n\n
    ...    ${TEARDOWN ERROR}
    Continuable and regular failure
    Fail    This should not be executed

Several continuable failures and regular failure in nested UK
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) ${ERROR} in top level (with ∏ön ÄßÇïï €§)\n\n
    ...    2) ${EXC}: 1\n\n
    ...    3) ${EXC}: 2\n\n
    ...    4) ${EXC}: 3\n\n
    ...    5) ${ERROR} in top level after nesting (with ∏ön ÄßÇïï €§)\n\n
    ...    6) ${EXC}: first level 1\n\n
    ...    7) ${EXC}: Can be continued in top level (with ∏ön ÄßÇïï €§)\n\n
    ...    8) ${EXC}: 1\n\n
    ...    9) ${EXC}: 2\n\n
    ...    10) ${EXC}: 3\n\n
    ...    11) ${EXC}: Can be continued in top level after nesting (with ∏ön ÄßÇïï €§)\n\n
    ...    12) ${EXC}: first level 2\n\n
    ...    13) ${EXC}: one\n\n
    ...    14) ${EXC}: two\n\n
    ...    15) Stop!!\n\n
    ...    ${TEARDOWN ERROR}
    Continuable Failure In Nested UK
    Continuable and regular failure in nested UK
    Fail    This should not be executed

Continue when setting variables
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) ${ERROR}\n\n
    ...    2) ${ERROR}\n\n
    ...    3) ${ERROR}\n\n
    ...    4) No jokes\n\n
    ...    ${TEARDOWN ERROR}
    ${ret}=    Raise Continuable Failure
    Should Be Equal    ${ret}    ${None}
    ${r1}    ${r2}    ${r3}=    Raise Continuable Failure
    Should Be True    ${r1} == ${r2} == ${r3} == None
    @{list}=    Raise Continuable Failure
    Should Be True    @{list} == []
    ${notset} =    Fail    No jokes

Continuable failure in user keyword returning value
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) Continuable failure\n\n
    ...    2) Another continuable failure\n\n
    ...    3) Continuable failure\n\n
    ...    ${TEARDOWN ERROR}
    ${ret} =    Continuable failure in user keyword returning value
    Should Be Equal    ${ret}    return value
    ${ret} =    Continuable failure in nested user keyword returning value
    Should Be Equal    ${ret}    return value 2

Continue in test setup
    [Documentation]    FAIL Setup failed:\n${ERROR WITH TEARDOWN}
    [Setup]    Continuable Failure In User Keyword In Test Setup
    Fail    This should not be executed (with ∏ön ÄßÇïï €§)

Continue in test teardown
    [Documentation]    FAIL Teardown failed:\n${ERROR WITH TEARDOWN}
    No operation
    [Teardown]    Continuable Failure In User Keyword In Test Teardown

Continue many times in test setup and teardown
    [Documentation]    FAIL Setup failed:\n
    ...    ${HEADER}\n\n
    ...    1) ${EXC}: 1\n\n
    ...    2) ${EXC}: 2\n\n
    ...    3) ${EXC}: 3\n\n
    ...    Also teardown failed:\n
    ...    ${HEADER}\n\n
    ...    1) ${EXC}: 1\n\n
    ...    2) ${EXC}: 2\n\n
    ...    3) ${EXC}: 3\n\n
    ...    ${TEARDOWN ERROR}
    [Setup]    Several Continuable Failures In User Keyword In Test Setup
    Fail    This should not be executed
    [Teardown]    Several Continuable Failures In User Keyword In Test Teardown

Continue in for loop
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) ContinuableApocalypseException: 0\n\n
    ...    2) ContinuableApocalypseException: 1\n\n
    ...    3) ContinuableApocalypseException: 2\n\n
    ...    4) ContinuableApocalypseException: 3\n\n
    ...    5) ContinuableApocalypseException: 4\n\n
    ...    ${TEARDOWN ERROR}
    FOR    ${i}    IN RANGE    0    5
        Raise Continuable Failure    ${i}
        Log    This should be executed inside for loop
    END
    Log    This should be executed after for loop

Continuable and regular failure in for loop
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) ContinuableApocalypseException: janne\n\n
    ...    2) ContinuableApocalypseException: jussi\n\n
    ...    3) ContinuableApocalypseException: keijo\n\n
    ...    4) keijo == keijo\n\n
    ...    ${TEARDOWN ERROR}
    FOR    ${name}    IN    janne    jussi    keijo    juha    jooseppi
        Raise Continuable Failure    ${name}
        Should Not Be Equal    ${name}    keijo
    END
    Fail    Should not be executed

robot.api.ContinuableFailure
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2\n\n
    ...    3) 3\n\n
    ...    ${TEARDOWN ERROR}
    Raise Continuable Failure    1    standard=True
    Raise Continuable Failure    2    standard=True
    Fail    3
    Raise Continuable Failure    Should not be executed

*** Keywords ***
Continuable Failure In User Keyword In ${where}
    Raise Continuable Failure
    Log    This should be executed in ${where}

Several Continuable Failures In User Keyword In ${where}
    Raise Continuable Failure    1
    Log    This should be executed in ${where} (with ∏ön ÄßÇïï €§)
    Raise Continuable Failure    2
    Log    This should also be executed in ${where}
    Raise Continuable Failure    3
    Log    This too should also be executed in ${where}

Continuable Failure In Nested UK
    Raise Continuable Failure    Can be continued in top level (with ∏ön ÄßÇïï €§)
    Log    This should be executed in Top Level UK (with ∏ön ÄßÇïï €§)
    Several Continuable Failures In User Keyword In Nested UK
    Raise Continuable Failure    Can be continued in top level after nesting (with ∏ön ÄßÇïï €§)

Continuable and regular failure in nested UK
    Raise Continuable Failure    first level 1
    Continuable Failure In Nested UK
    Raise Continuable Failure    first level 2
    Continuable and regular failure
    Fail    This should not be executed

Continuable and regular failure
    Raise Continuable Failure    one
    Raise Continuable Failure    two
    Log    This should be executed in Nested UK (with ∏ön ÄßÇïï €§)
    Fail    Stop!!

Continuable failure in user keyword returning value
    Run Keyword And Continue On Failure   Fail    Continuable failure
    ${ret} =    Set Variable    return value
    Should Be Equal    ${ret}    return value
    RETURN    ${ret}

Continuable failure in nested user keyword returning value
    Run Keyword And Continue On Failure   Fail    Another continuable failure
    ${ret} =    Continuable failure in user keyword returning value
    Should Be Equal    ${ret}    return value
    RETURN    ${ret} 2
