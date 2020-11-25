*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/else_if.robot
Resource          atest_resource.robot

*** Test Cases ***
Else if condition 1 passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    if        PASS
    Check Branch Status    ${tc.kws[1]}    elseif    NOT_RUN
    Check Branch Status    ${tc.kws[2]}    else      NOT_RUN

Else if condition 2 passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    if        NOT_RUN
    Check Branch Status    ${tc.kws[1]}    elseif    PASS
    Check Branch Status    ${tc.kws[2]}    else      NOT_RUN

Else if else passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    if        NOT_RUN
    Check Branch Status    ${tc.kws[1]}    elseif    NOT_RUN
    Check Branch Status    ${tc.kws[2]}    else      PASS

Else if condition 1 failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    if        FAIL
    Length Should Be       ${tc.kws}       1

Else if condition 2 failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    if        NOT_RUN
    Check Branch Status    ${tc.kws[1]}    elseif    FAIL
    Length Should Be       ${tc.kws}       2

Else if else failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.kws[0]}    if        NOT_RUN
    Check Branch Status    ${tc.kws[1]}    elseif    NOT_RUN
    Check Branch Status    ${tc.kws[2]}    else      FAIL

*** Keywords ***
Check Branch Status
    [Arguments]    ${branch}    ${type}    ${status}
    Should Be Equal    ${branch.type}    ${type}
    Should Be Equal    ${branch.status}    ${status}
