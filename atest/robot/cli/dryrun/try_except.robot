*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/try_except.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
TRY
    ${tc} =    Check Test Case    ${TESTNAME}
    Check TRY Data        ${tc.body[0].body[0]}
    Check Keyword Data    ${tc.body[0].body[0].body[0]}    resource.Simple UK
    Check Keyword Data    ${tc.body[0].body[0].body[0].body[0]}    BuiltIn.Log    args=Hello from UK    status=NOT RUN
    Check Keyword Data    ${tc.body[0].body[1].body[0]}    BuiltIn.Log    args=handling it    status=NOT RUN
    Check Keyword Data    ${tc.body[0].body[2].body[0]}    BuiltIn.Log    args=in the else    status=NOT RUN
    Check Keyword Data    ${tc.body[0].body[3].body[0]}    BuiltIn.Log    args=in the finally    status=NOT RUN
    Check TRY Data        ${tc.body[1].body[0]}            status=FAIL
    Check Keyword Data    ${tc.body[1].body[0].body[0]}    resource.Anarchy in the UK    status=FAIL    args=1, 2
