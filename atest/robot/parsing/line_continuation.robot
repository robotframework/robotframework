*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    parsing/line_continuation.robot
Resource        atest_resource.robot

*** Test Cases ***
Multiline suite documentation and metadata
    Should Be Equal    ${SUITE.doc}    First row.\nSecond row.\n\nSecond paragraph\n!
    Should Be Equal    ${SUITE.metadata['Name']}    1.1\n1.2\n\n2.1\n2.2\n2.3\n\n3.1

Multiline suite level settings
    Should Contain Tags   ${SUITE.tests[0]}
    ...    ...    t1    t2    t3    t4    t5    t6    t7    t8    t9
    Check Log Message    ${SUITE.tests[0].teardown.msgs[0]}    1st
    Check Log Message    ${SUITE.tests[0].teardown.msgs[1]}    ${EMPTY}
    Check Log Message    ${SUITE.tests[0].teardown.msgs[2]}    2nd last
    Check Log Message    ${SUITE.tests[0].teardown.msgs[3]}    ${EMPTY}
    Length Should Be    ${SUITE.tests[0].teardown.msgs}    4

Multiline import
    Check Test Case    ${TEST NAME}

Multiline variables
    Check Test Case    ${TEST NAME}

Multiline arguments with library keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    one
    Check Log Message    ${tc.kws[0].msgs[1]}    two
    Check Log Message    ${tc.kws[0].msgs[2]}    three
    Check Log Message    ${tc.kws[0].msgs[3]}    ${EMPTY}
    Check Log Message    ${tc.kws[0].msgs[4]}    four
    Check Log Message    ${tc.kws[0].msgs[5]}    five

Multiline arguments with user keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1
    Check Log Message    ${tc.kws[0].kws[0].msgs[1]}    ${EMPTY}
    Check Log Message    ${tc.kws[0].kws[0].msgs[2]}    2
    Check Log Message    ${tc.kws[0].kws[0].msgs[3]}    3
    Check Log Message    ${tc.kws[0].kws[0].msgs[4]}    4
    Check Log Message    ${tc.kws[0].kws[0].msgs[5]}    5

Multiline assignment
    Check Test Case    ${TEST NAME}

Multiline in user keyword
    Check Test Case    ${TEST NAME}

Multiline test settings
    ${tc} =    Check Test Case    ${TEST NAME}
    @{expected} =   Evaluate    ['my'+str(i) for i in range(1,6)]
    Should Contain Tags   ${tc}    @{expected}
    Should Be Equal    ${tc.doc}    One.\nTwo.\nThree.\n\n${SPACE*32}Second paragraph.
    Check Log Message    ${tc.setup.msgs[0]}    first
    Check Log Message    ${tc.setup.msgs[1]}    ${EMPTY}
    Check Log Message    ${tc.setup.msgs[2]}    last

Multiline user keyword settings and control structures
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    Multiline user keyword settings and control structures
    ...    \${x}    1, 2    tags=keyword, tags
    Check Log Message    ${tc.kws[0].teardown.msgs[0]}    Bye!

Multiline FOR Loop declaration
    Check Test Case    ${TEST NAME}

Multiline in FOR loop body
    Check Test Case    ${TEST NAME}

Escaped empty cells before line continuation do not work
    Error in file    0    parsing/line_continuation.robot    11
    ...    Non-existing setting '\\'.
    Error in file    1    parsing/line_continuation.robot    43
    ...    Setting variable '\\' failed: Invalid variable name '\\'.
    Check Test Case    Invalid usage in keyword call

Invalid multiline usage
    Check Test Case    Invalid Usage In Test
    Check Test Case    Invalid Usage In User Keyword
