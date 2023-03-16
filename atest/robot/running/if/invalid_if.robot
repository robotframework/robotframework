*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/invalid_if.robot
Test Template     Branch statuses should be
Resource          atest_resource.robot

*** Test Cases ***
IF without condition
    FAIL

IF without condition with ELSE
    FAIL    NOT RUN

IF with invalid condition
    FAIL

IF with invalid condition with ELSE
    FAIL    NOT RUN

IF condition with non-existing ${variable}
    FAIL    NOT RUN

IF condition with non-existing $variable
    FAIL    NOT RUN

ELSE IF with invalid condition
    NOT RUN    NOT RUN    FAIL    NOT RUN    NOT RUN

Recommend $var syntax if invalid condition contains ${var}
    FAIL    index=1

IF without END
    FAIL

Invalid END
    FAIL

IF with wrong case
    [Template]    NONE
    Check Test Case    ${TEST NAME}

ELSE IF without condition
    FAIL    NOT RUN    NOT RUN

ELSE IF with multiple conditions
    [Template]    NONE
    ${tc} =    Branch statuses should be    FAIL    NOT RUN    NOT RUN
    Should Be Equal    ${tc.body[0].body[1].condition}    \${False}, ooops, \${True}

ELSE with condition
    FAIL    NOT RUN

IF with empty body
    FAIL

ELSE with empty body
    FAIL    NOT RUN

ELSE IF with empty body
    FAIL    NOT RUN    NOT RUN

ELSE after ELSE
    FAIL    NOT RUN    NOT RUN

ELSE IF after ELSE
    FAIL    NOT RUN    NOT RUN

Dangling ELSE
    [Template]    Check Test Case
    ${TEST NAME}

Dangling ELSE inside FOR
    [Template]    Check Test Case
    ${TEST NAME}

Dangling ELSE inside WHILE
    [Template]    Check Test Case
    ${TEST NAME}

Dangling ELSE IF
    [Template]    Check Test Case
    ${TEST NAME}

Dangling ELSE IF inside FOR
    [Template]    Check Test Case
    ${TEST NAME}

Dangling ELSE IF inside WHILE
    [Template]    Check Test Case
    ${TEST NAME}

Dangling ELSE IF inside TRY
    [Template]    Check Test Case
    ${TEST NAME}

Invalid IF inside FOR
    FAIL

Multiple errors
    FAIL    NOT RUN    NOT RUN    NOT RUN    NOT RUN

Invalid data causes syntax error
    [Template]    Check Test Case
    ${TEST NAME}

Invalid condition causes normal error
    [Template]    Check Test Case
    ${TEST NAME}

Non-existing variable in condition causes normal error
    [Template]    Check Test Case
    ${TEST NAME}

*** Keywords ***
Branch statuses should be
    [Arguments]    @{statuses}    ${index}=0
    ${tc} =    Check Test Case    ${TESTNAME}
    ${if} =    Set Variable    ${tc.body}[${index}]
    Should Be Equal    ${if.status}    FAIL
    FOR    ${branch}    ${status}    IN ZIP    ${if.body}    ${statuses}    mode=STRICT
        Should Be Equal    ${branch.status}    ${status}
    END
    RETURN    ${tc}
