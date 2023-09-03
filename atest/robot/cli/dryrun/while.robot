*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/while.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
WHILE
    ${tc} =    Check Test Case    ${TESTNAME}
    Length should be    ${tc.body[1].body}             1
    Length should be    ${tc.body[1].body[0].body}     3
    Length should be    ${tc.body[2].body}             1
    Length should be    ${tc.body[1].body[0].body}     3
    Length should be    ${tc.body[3].body}             3
    Length should be    ${tc.body[3].body[0].body}     0
    Length should be    ${tc.body[3].body[1].body}     1
    Length should be    ${tc.body[3].body[2].body}     0

WHILE with BREAK and CONTINUE
    ${tc} =    Check Test Case    ${TESTNAME}
    Length should be    ${tc.body[1].body}             1
    Length should be    ${tc.body[2].body}             1
