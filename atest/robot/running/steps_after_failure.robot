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
    Should Not Be Run    ${tc.body[1].body[0].body}
    Should Not Be Run    ${tc.body[1].body[1].body}

FOR after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}
    Should Not Be Run    ${tc.body[1].body}
    Should Not Be Run    ${tc.body[1].body[0].body}    2

Nested control structure after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}    2
    Should Be Equal      ${tc.body[1].type}    FOR
    Should Not Be Run    ${tc.body[1].body}    1
    Should Be Equal      ${tc.body[1].body[0].type}    FOR ITERATION
    Should Not Be Run    ${tc.body[1].body[0].body}    2
    Should Be Equal      ${tc.body[1].body[0].body[0].type}    IF/ELSE ROOT
    Should Not Be Run    ${tc.body[1].body[0].body[0].body}    2
    Should Be Equal      ${tc.body[1].body[0].body[0].body[0].type}    IF
    Should Not Be Run    ${tc.body[1].body[0].body[0].body[0].body}    2
    Should Be Equal      ${tc.body[1].body[0].body[0].body[0].body[0].type}    FOR
    Should Not Be Run    ${tc.body[1].body[0].body[0].body[0].body[0].body}    1
    Should Be Equal      ${tc.body[1].body[0].body[0].body[0].body[0].body[0].type}    FOR ITERATION
    Should Not Be Run    ${tc.body[1].body[0].body[0].body[0].body[0].body[0].body}    3
    Should Be Equal      ${tc.body[1].body[0].body[0].body[0].body[0].body[0].body[0].type}    KEYWORD
    Should Be Equal      ${tc.body[1].body[0].body[0].body[0].body[0].body[0].body[1].type}    KEYWORD
    Should Be Equal      ${tc.body[1].body[0].body[0].body[0].body[0].body[0].body[2].type}    KEYWORD
    Should Be Equal      ${tc.body[1].body[0].body[0].body[0].body[1].type}    KEYWORD
    Should Be Equal      ${tc.body[1].body[0].body[0].body[1].type}    ELSE
    Should Not Be Run    ${tc.body[1].body[0].body[0].body[1].body}    1
    Should Be Equal      ${tc.body[1].body[0].body[0].body[1].body[0].type}    KEYWORD
    Should Be Equal      ${tc.body[1].body[0].body[1].type}    KEYWORD
    Should Be Equal      ${tc.body[2].type}    KEYWORD

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
    Should Not Be Run    ${tc.body[0].body[0].body[1:]}
    Should Not Be Run    ${tc.body[0].body[1].body}
    Should Not Be Run    ${tc.body[1:]}

Failure in ELSE IF branch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[0].body[0].body}
    Should Not Be Run    ${tc.body[0].body[1].body[1:]}
    Should Not Be Run    ${tc.body[0].body[2].body}
    Should Not Be Run    ${tc.body[1:]}

Failure in ELSE branch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[0].body[0].body}
    Should Not Be Run    ${tc.body[0].body[1].body[1:]}
    Should Not Be Run    ${tc.body[1:]}

Failure in FOR iteration
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc.body[1:]}
    Length Should Be     ${tc.body[0].body}    1
    Should Not Be Run    ${tc.body[0].body[0].body[1:]}

*** Keywords ***
Should Not Be Run
    [Arguments]    ${steps}    ${expected count}=1
    FOR    ${step}    IN    @{steps}
        Should Be Equal    ${step.status}    NOT RUN
    END
    Length Should Be    ${steps}    ${expected count}
