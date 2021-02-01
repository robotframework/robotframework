*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/steps_after_failure.robot
Resource          atest_resource.robot

*** Test Cases ***
Library keyword after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[2:]}    5
    Check Log Message    ${tc.teardown.msgs[0]}    This is run

User keyword after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}

IF after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}

FOR after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}

Non-existing keyword after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}

Invalid keyword usage after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}

Failure in user keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}
    Should Not Be Run    ${tc.body[0].body[1:]}    2

Failure in IF branch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}
    Should Not Be Run    ${tc.body[0].body[1:]}
    Should Be True       ${tc.body[0].orelse}
    Should Not Be Run    ${tc.body[0].orelse.body}      1

Failure in ELSE IF branch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}
    Should Not Be Run    ${tc.body[0].body}    1
    Should Not Be Run    ${tc.body[0].orelse.body[1:]}
    Should Be True       ${tc.body[0].orelse.orelse}
    Should Not Be Run    ${tc.body[0].orelse.orelse.body}    1

Failure in ELSE branch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}
    Should Not Be Run    ${tc.body[0].body}    1
    Should Not Be Run    ${tc.body[0].orelse.body[1:]}

Failure in FOR iteration
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}
    Length Should Be     ${tc.body[0].body}    1
    Should Not Be Run    ${tc.body[0].body[0].body[1:]}


*** Keywords ***
Should Not Be Run
    [Arguments]    ${steps}    ${expected count}=1
    FOR    ${step}    IN    @{steps}
        Should Be Equal    ${step.status}    NOT_RUN
    END
    Length Should Be    ${steps}    ${expected count}
