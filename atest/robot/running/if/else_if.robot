*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/else_if.robot
Resource          atest_resource.robot

*** Test Cases ***
Else if condition 1 passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    IF         PASS
    Check Branch Status    ${tc.kws[1]}    ELSE IF    NOT_RUN
    Check Branch Status    ${tc.kws[2]}    ELSE       NOT_RUN

Else if condition 2 passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    IF         NOT_RUN
    Check Branch Status    ${tc.kws[1]}    ELSE IF    PASS
    Check Branch Status    ${tc.kws[2]}    ELSE       NOT_RUN

Else if else passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    IF         NOT_RUN
    Check Branch Status    ${tc.kws[1]}    ELSE IF    NOT_RUN
    Check Branch Status    ${tc.kws[2]}    ELSE       PASS

Else if condition 1 failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    IF         FAIL
    Length Should Be       ${tc.kws}       1

Else if condition 2 failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    IF         NOT_RUN
    Check Branch Status    ${tc.kws[1]}    ELSE IF    FAIL
    Length Should Be       ${tc.kws}       2

Else if else failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    IF         NOT_RUN
    Check Branch Status    ${tc.kws[1]}    ELSE IF    NOT_RUN
    Check Branch Status    ${tc.kws[2]}    ELSE       FAIL

*** Keywords ***
Check Branch Status
    [Arguments]    ${branch}    ${type}    ${status}
    Should Be Equal    ${branch.type}    ${type}
    Should Be Equal    ${branch.status}    ${status}
