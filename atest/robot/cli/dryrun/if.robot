*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/if.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
IF will not recurse in dry run
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Branch Statuses    ${tc.kws[0]}                  Recursive if         PASS
    Check Branch Statuses    ${tc.kws[0].kws[0].kws[0]}    Recursive if         NOT_RUN

ELSE IF will not recurse in dry run
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Branch Statuses    ${tc.kws[0]}                  Recursive else if    PASS
    Check Branch Statuses    ${tc.kws[0].kws[1].kws[0]}    Recursive else if    NOT_RUN

ELSE will not recurse in dry run
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Branch Statuses    ${tc.kws[0]}                  Recursive else       PASS
    Check Branch Statuses    ${tc.kws[0].kws[2].kws[0]}    Recursive else       NOT_RUN

Dryrun fail inside of IF
    Check Test Case    ${TESTNAME}

Dryrun fail inside of ELSE IF
    Check Test Case    ${TESTNAME}

Dryrun fail inside of ELSE
    Check Test Case    ${TESTNAME}

Dryrun fail invalid IF in non executed branch
    Check Test Case    ${TESTNAME}

Dryrun fail invalid ELSE in non executed branch
    Check Test Case    ${TESTNAME}

Dryrun fail invalid ELSE IF in non executed branch
    Check Test Case    ${TESTNAME}

Dryrun fail empty if in non executed branch
    Check Test Case    ${TESTNAME}

*** Keywords ***
Check Branch Statuses
    [Arguments]    ${kw}    ${name}    ${status}
    Should Be Equal    ${kw.name}             ${name}
    Should Be Equal    ${kw.kws[0].type}      IF
    Should Be Equal    ${kw.kws[0].status}    ${status}
    Should Be Equal    ${kw.kws[1].type}      ELSE IF
    Should Be Equal    ${kw.kws[1].status}    ${status}
    Should Be Equal    ${kw.kws[2].type}      ELSE
    Should Be Equal    ${kw.kws[2].status}    ${status}
