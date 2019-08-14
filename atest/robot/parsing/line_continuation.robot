*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  parsing/line_continuation.robot
Resource        atest_resource.robot

*** Test Cases ***
Multiline suite documentation and metadata
    Should Be Equal    ${SUITE.doc}    First row.\nSecond row.\n\nSecond paragraph\n!\n!\n!
    Should Be Equal    ${SUITE.metadata['Name']}    1.1\n1.2\n\n2.1\n2.2\n2.3\n\n3.1

Multiline suite level settings
    Should Contain Tags   ${SUITE.tests[0]}
    ...    ...    t1    t2    t3    t4    t5    t6    t7    t8    t9
    Check Log Message    ${SUITE.tests[0].teardown.msgs[0]}    1st
    Check Log Message    ${SUITE.tests[0].teardown.msgs[1]}    2nd last
    Length Should Be    ${SUITE.tests[0].teardown.msgs}    2

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
    @{expected} =   Evaluate    ['my'+str(i) for i in range(1,6)]
    Should Contain Tags   ${tc}    @{expected}
    Should Be Equal    ${tc.doc}    One.\nTwo.\nThree.\n\nSecond paragraph.
    Check Log Message    ${tc.setup.msgs[0]}    first
    Check Log Message    ${tc.setup.msgs[1]}    last

Multiline user keyword settings
    Check Test Case    ${TEST NAME}

Multiline for Loop declaration
    Check Test Case    ${TEST NAME}

Multiline in for loop body
    Check Test Case    ${TEST NAME}

Escaped empty cells before line continuation are deprecated
    [Template]    Check Escaped Leading Empty Cell Deprecation
    1
    10
    12

Line continuation without value is deprecated
    [Documentation]    Except for Documentation and Metadata
    [Template]    Check Line Continuation Alone Deprecation
    2     In 'Default Tags' setting
    3     In 'Test Teardown' setting
    4     In 'Test Teardown' setting
    5     In 'Variables' section
    6     In 'Variables' section
    7     In 'Variables' section
    8     In 'Variables' section
    9     Invalid syntax in test case 'Multiline arguments with library keyword'
    11    Invalid syntax in test case 'Multiline arguments with user keyword'
    13    Invalid syntax in test case 'Multiline test settings': In '[Tags]' setting
    14    Invalid syntax in test case 'Multiline test settings': In '[Setup]' setting
    15    Invalid syntax in test case 'Invalid usage in test and user keyword'
    16    Invalid syntax in keyword 'Multiline user keyword settings': In '[Return]' setting
    17    Invalid syntax in keyword 'Invalid usage in UK'

Invalid multiline usage
    [Setup]    Check Test Case    Invalid Usage In Test And User Keyword
    [Template]    Check Multiline Error
    0     Non-existing setting '...'.
    -1    Setting variable '...' failed: Invalid variable name '...'.

*** Keywords ***
Check Escaped Leading Empty Cell Deprecation
    [Arguments]    ${index}
    ${message} =    Catenate
    ...    Escaping empty cells with '\\' before line continuation marker '...'
    ...    is deprecated. Remove escaping before Robot Framework 3.2.
    Check Multiline Error    ${index}    ${message}    WARN

Check Line Continuation Alone Deprecation
    [Arguments]    ${index}    ${prefix}
    ${message} =    Catenate
    ...    ${prefix}:
    ...    Ignoring lines with only continuation marker '...' is deprecated.
    Check Multiline Error    ${index}    ${message}    WARN

Check Multiline Error
    [Arguments]    ${index}    ${message}    ${level}=ERROR
    ${path} =    Normalize Path    ${DATADIR}/parsing/line_continuation.robot
    Check Log Message    ${ERRORS}[${index}]
    ...    Error in file '${path}': ${message}    ${level}
