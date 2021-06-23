*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/for.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
FOR
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate loops      ${tc}                      4
    Length should be    ${tc.kws[2].kws}           3
    Length should be    ${tc.kws[2].kws[0].kws}    0
    Length should be    ${tc.kws[2].kws[1].kws}    1
    Length should be    ${tc.kws[2].kws[2].kws}    0

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
    Length should be    ${tc.kws}                  ${kws}
    Length should be    ${tc.kws[0].kws}           1
    Length should be    ${tc.kws[0].kws[0].kws}    2
    Length should be    ${tc.kws[1].kws}           1
    Length should be    ${tc.kws[1].kws[0].kws}    1
