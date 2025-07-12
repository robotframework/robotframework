*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/while.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
WHILE
    ${tc} =    Check Test Case    ${TESTNAME}
    Length should be    ${tc[1].body}        1
    Length should be    ${tc[1, 0].body}     3
    Length should be    ${tc[2].body}        1
    Length should be    ${tc[1, 0].body}     3
    Length should be    ${tc[3].body}        3
    Length should be    ${tc[3, 0].body}     0
    Length should be    ${tc[3, 1].body}     1
    Length should be    ${tc[3, 2].body}     0

WHILE with BREAK and CONTINUE
    ${tc} =    Check Test Case    ${TESTNAME}
    Length should be    ${tc[1].body}             1
    Length should be    ${tc[2].body}             1
