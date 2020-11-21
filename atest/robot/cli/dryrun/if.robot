*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/if.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
IF will not recurse in dry run
    Check Test Case    ${TESTNAME}

ELSE IF will not recurse in dry run
    ${tc}=  Check Test Case    ${TESTNAME}
    Should be equal  ${tc.kws[0].kws[0].type}  if
    Should be equal  ${tc.kws[0].kws[1].type}  else if
    Should be equal  ${tc.kws[0].kws[2].type}  else

ELSE will not recurse in dry run
    Check Test Case    ${TESTNAME}

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