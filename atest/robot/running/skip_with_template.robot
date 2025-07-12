*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    running/skip_with_template.robot
Resource        atest_resource.robot

*** Test Cases ***
SKIP + PASS -> PASS
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    SKIP    Skipped
    Status Should Be    ${tc[1]}    PASS

FAIL + ANY -> FAIL
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    PASS
    Status Should Be    ${tc[1]}    SKIP    Skipped
    Status Should Be    ${tc[2]}    PASS
    Status Should Be    ${tc[3]}    FAIL    Failed
    Status Should Be    ${tc[4]}    SKIP    Skipped

Only SKIP -> SKIP
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    SKIP    Skipped
    Status Should Be    ${tc[1]}    SKIP    Skipped

IF w/ SKIP + PASS -> PASS
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    PASS
    Status Should Be    ${tc[1]}    SKIP    Skipped
    Status Should Be    ${tc[2]}    PASS

IF w/ FAIL + ANY -> FAIL
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    FAIL    Failed
    Status Should Be    ${tc[1]}    SKIP    Skipped
    Status Should Be    ${tc[2]}    PASS

IF w/ only SKIP -> SKIP
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    SKIP    All iterations skipped.
    Status Should Be    ${tc[1]}    SKIP    Skip 3
    Status Should Be    ${tc[2]}    SKIP    Skip 4

FOR w/ SKIP + PASS -> PASS
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    PASS
    Status Should Be    ${tc[1]}    SKIP    just once
    Status Should Be    ${tc[2]}    PASS

FOR w/ FAIL + ANY -> FAIL
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    FAIL    Several failures occurred:\n\n1) a\n\n2) b
    Status Should Be    ${tc[1]}    SKIP    just once
    Status Should Be    ${tc[2]}    PASS

FOR w/ only SKIP -> SKIP
    ${tc} =    Check Test Case    ${TEST NAME}
    Status Should Be    ${tc[0]}    SKIP    All iterations skipped.
    Status Should Be    ${tc[1]}    SKIP    just once

Messages in test body are ignored
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0]}          Hello 'Messages in test body are ignored', says listener!
    Check Log Message    ${tc[1, 0, 0]}    Library listener adds messages to body of this test.
    Check Log Message    ${tc[2, 0, 0]}    This iteration is skipped!    SKIP
    Check Log Message    ${tc[3, 0, 0]}    This iteration passes!
    Check Log Message    ${tc[4]}          Bye 'Messages in test body are ignored', says listener!

*** Keywords ***
Status Should Be
    [Arguments]    ${item}    ${status}    ${message}=
    Should Be Equal    ${item.status}     ${status}
    Should Be Equal    ${item.message}    ${message}
