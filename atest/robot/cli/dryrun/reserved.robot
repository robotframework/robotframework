*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/reserved.robot
Resource          atest_resource.robot

*** Test Cases ***
For
    Check Test Case    ${TESTNAME}

Valid END after For
    Check Test Case    ${TESTNAME}

If
    Check Test Case    ${TESTNAME}

Else If
    Check Test Case    ${TESTNAME}

Else
    Check Test Case    ${TESTNAME}

Else inside valid IF
    Check Test Case    ${TESTNAME}

Else If inside valid IF
    Check Test Case    ${TESTNAME}

End
    Check Test Case    ${TESTNAME}

End after valid FOR header
    Check Test Case    ${TESTNAME}

End after valid If header
    Check Test Case    ${TESTNAME}

Reserved inside FOR
    Check Test Case    ${TESTNAME}

Reserved inside IF
    Check Test Case    ${TESTNAME}
