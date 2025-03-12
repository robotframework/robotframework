*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/for.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
FOR
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate loops      ${tc}               4
    Length should be    ${tc[2].body}       3
    Length should be    ${tc[2, 0].body}    0
    Length should be    ${tc[2, 1].body}    1
    Length should be    ${tc[2, 2].body}    0

FOR IN RANGE
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate loops    ${tc}

FOR IN ENUMERATE
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate loops    ${tc}

FOR IN ZIP
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate loops    ${tc}

*** Keywords ***
Validate loops
    [Arguments]    ${tc}    ${kws}=3
    Length should be    ${tc.body}          ${kws}
    Length should be    ${tc[0].body}       1
    Length should be    ${tc[0, 0].body}    2
    Length should be    ${tc[1].body}       1
    Length should be    ${tc[1, 0].body}    1
