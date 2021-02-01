*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/else_if.robot
Resource          atest_resource.robot

*** Test Cases ***
Else if condition 1 passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.body[0]}                  if        PASS
    Check Branch Status    ${tc.body[0].orelse}           elseif    NOT_RUN
    Check Branch Status    ${tc.body[0].orelse.orelse}    else      NOT_RUN

Else if condition 2 passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.body[0]}                  if        NOT_RUN
    Check Branch Status    ${tc.body[0].orelse}           elseif    PASS
    Check Branch Status    ${tc.body[0].orelse.orelse}    else      NOT_RUN

Else if else passes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.body[0]}                  if        NOT_RUN
    Check Branch Status    ${tc.body[0].orelse}           elseif    NOT_RUN
    Check Branch Status    ${tc.body[0].orelse.orelse}    else      PASS

Else if condition 1 failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.body[0]}                  if        FAIL
    Check Branch Status    ${tc.body[0].orelse}           elseif    NOT_RUN

Else if condition 2 failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.body[0]}                  if        NOT_RUN
    Check Branch Status    ${tc.body[0].orelse}           elseif    FAIL
    Check Branch Status    ${tc.body[0].orelse.orelse}    else      NOT_RUN

Else if else failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.body[0]}                  if        NOT_RUN
    Check Branch Status    ${tc.body[0].orelse}           elseif    NOT_RUN
    Check Branch Status    ${tc.body[0].orelse.orelse}    else      FAIL

Invalid
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Branch Status    ${tc.body[0]}                  if        FAIL
    Should Not Be True     ${tc.body[0].orelse}

*** Keywords ***
Check Branch Status
    [Arguments]    ${branch}    ${type}    ${status}
    Should Be Equal    ${branch.type}    ${type}
    Should Be Equal    ${branch.branch_status}    ${status}
    IF   $status != 'NOT_RUN'
        Should Be Equal    ${branch.status}    ${status}
    END
