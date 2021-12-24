*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/if.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
IF will not recurse in dry run
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Branch Statuses    ${tc.body[0]}                            Recursive if         PASS
    Check Branch Statuses    ${tc.body[0].body[0].body[0].body[0]}    Recursive if         NOT RUN

ELSE IF will not recurse in dry run
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Branch Statuses    ${tc.body[0]}                            Recursive else if    PASS
    Check Branch Statuses    ${tc.body[0].body[0].body[1].body[0]}    Recursive else if    NOT RUN

ELSE will not recurse in dry run
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Branch Statuses    ${tc.body[0]}                            Recursive else       PASS
    Check Branch Statuses    ${tc.body[0].body[0].body[2].body[0]}    Recursive else       NOT RUN

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

Dryrun fail empty IF in non executed branch
    Check Test Case    ${TESTNAME}

*** Keywords ***
Check Branch Statuses
    [Arguments]    ${kw}    ${name}    ${status}
    Should Be Equal    ${kw.name}                      ${name}
    Should Be Equal    ${kw.body[0].body[0].type}      IF
    Should Be Equal    ${kw.body[0].body[0].status}    ${status}
    Should Be Equal    ${kw.body[0].body[1].type}      ELSE IF
    Should Be Equal    ${kw.body[0].body[1].status}    ${status}
    Should Be Equal    ${kw.body[0].body[2].type}      ELSE
    Should Be Equal    ${kw.body[0].body[2].status}    ${status}
