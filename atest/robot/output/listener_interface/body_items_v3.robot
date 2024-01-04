*** Settings ***
Suite Setup       Run Tests    --listener ${DATADIR}/${MODIFIER}    ${SOURCE}
Resource          atest_resource.robot

*** Variables ***
${SOURCE}         output/listener_interface/body_items_v3/tests.robot
${MODIFIER}       output/listener_interface/body_items_v3/Modifier.py
@{ALL TESTS}      Library keyword    User keyword    Non-existing keyword
...               Empty keyword    Duplicate keyword    Invalid keyword
...               IF    TRY    FOR    WHILE    VAR    RETURN
...               Invalid syntax    Run Keyword

*** Test Cases ***
Modify library keyword
    Check Test Case    Library keyword         FAIL    Expected state to be 'initial', but it was 'set by listener'.

Modify user keyword
    Check Test Case    User keyword            FAIL    Failed by listener once!
    Check Test Case    Empty keyword           PASS    ${EMPTY}

Modify invalid keyword
    Check Test Case    Non-existing keyword    PASS    ${EMPTY}
    Check Test Case    Duplicate keyword       PASS    ${EMPTY}
    Check Test Case    Invalid keyword         PASS    ${EMPTY}

Modify keyword results
    ${tc} =    Get Test Case    Invalid keyword
    Check Keyword Data    ${tc.body[0]}    Invalid keyword
    ...    args=\${secret}
    ...    tags=end, fixed, start
    ...    doc=Results can be modified both in start and end!

Modify FOR
    ${tc} =    Check Test Case    FOR       FAIL    Listener failed me at 'b'!
    Length Should Be    ${tc.body[0].body}                     2
    Should Be Equal     ${tc.body[0].assign}[0]                secret
    Should Be Equal     ${tc.body[0].body[0].assign}[\${x}]    xxx
    Should Be Equal     ${tc.body[0].body[1].assign}[\${x}]    xxx

Modify WHILE
    ${tc} =    Check Test Case    WHILE     FAIL    Fail at iteration 10.
    Length Should Be    ${tc.body[0].body}                     10

Modify IF
    ${tc} =    Check Test Case    IF        FAIL    Executed!
    Should Be Equal     ${tc.body[0].body[0].message}          Secret message!
    Should Be Equal     ${tc.body[0].body[1].message}          Secret message!
    Should Be Equal     ${tc.body[0].body[2].message}          Executed!

Modify TRY
    ${tc} =    Check Test Case    TRY       FAIL    Not caught!
    Length Should Be    ${tc.body[0].body}                     3

Modify VAR
    ${tc} =    Check Test Case    VAR       FAIL    value != VAR by listener
    Should Be Equal     ${tc.body[0].value}[0]                secret
    Should Be Equal     ${tc.body[1].value}[0]                secret

Modify RETURN
    ${tc} =    Check Test Case    RETURN    FAIL    RETURN by listener != value
    Should Be Equal     ${tc.body[0].body[1].values}[0]       secret

Validate that all methods are called correctly
    Run Tests    --variable VALIDATE_EVENTS:True    ${SOURCE}
    Should contain tests    ${SUITE}    @{ALL TESTS}
    Check Log Message    ${SUITE.teardown.messages[0]}    Listener StartEndBobyItemOnly is OK.
    Check Log Message    ${SUITE.teardown.messages[1]}    Listener SeparateMethods is OK.
    Check Log Message    ${SUITE.teardown.messages[2]}    Listener SeparateMethodsAlsoForKeywords is OK.
