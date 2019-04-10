*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  parsing/line_continuation.robot
Resource        atest_resource.robot

*** Test Cases ***
Multiline settings
    Should Be Equal    ${SUITE.doc}    This doc is one long string\n!\n!\n!\n!
    Should Contain Tags   ${SUITE.tests[0]}
    ...    ...    t1    t2    t3    t4    t5    t6    t7    t8    t9

Multiline import
    Check Test Case    ${TEST NAME}

Multiline variables
    Check Test Case    ${TEST NAME}

Multiline arguments with library keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    one
    Check Log Message    ${tc.kws[0].msgs[1]}    two
    Check Log Message    ${tc.kws[0].msgs[2]}    three
    Check Log Message    ${tc.kws[0].msgs[3]}    four
    Check Log Message    ${tc.kws[0].msgs[4]}    five

Multiline arguments with user keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    2
    Check Log Message    ${tc.kws[0].kws[0].msgs[2]}    3
    Check Log Message    ${tc.kws[0].kws[0].msgs[3]}    4
    Check Log Message    ${tc.kws[0].kws[0].msgs[4]}    5

Multiline assignment
    Check Test Case    ${TEST NAME}

Multiline in user keyword
    Check Test Case    ${TEST NAME}

Multiline test settings
    ${tc} =    Check Test Case    ${TEST NAME}
    @{expected}=   Evaluate    ['my'+str(i) for i in range(1,6)]
    Should Contain Tags   ${tc}    @{expected}
    Should Be Equal    ${tc.doc}    One.\nTwo.\nThree.\n\nSecond paragraph.

Multiline user keyword settings
    Check Test Case    ${TEST NAME}

Multiline for Loop declaration
    Check Test Case    ${TEST NAME}

Multiline in for loop body
    Check Test Case    ${TEST NAME}

Escaped empty cells before line continuation are deprecated
    ${message} =    Catenate
    ...    Escaping empty cells with '\\' before line continuation marker '...'
    ...    is deprecated. Remove escaping before Robot Framework 3.2.
    Check Multirow Error    1    ${message}    WARN
    Check Multirow Error    2    ${message}    WARN
    Check Multirow Error    3    ${message}    WARN
    Length Should Be    ${ERRORS}    5

Invalid multiline usage
    Check Multirow Error    0    Non-existing setting '...'.
    Check Multirow Error    4    Setting variable '...' failed: Invalid variable name '...'.
    Check Test Case    Invalid Usage In Test And User Keyword

*** Keywords ***
Check Multirow Error
    [Arguments]    ${index}    ${msg}    ${level}=ERROR
    ${path} =    Normalize Path    ${DATADIR}/parsing/line_continuation.robot
    Check Log Message    ${ERRORS}[${index}]
    ...    Error in file '${path}': ${msg}    ${level}
