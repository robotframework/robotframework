*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/documentation/
Resource          atest_resource.robot

*** Test Cases ***
Set test documentation
    ${tc} =    Check Test Doc    ${TESTNAME}     This has been set!\nTo several lines.
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test documentation to:\nThis has been set!\nTo several lines.

Replace test documentation
    ${tc} =    Check Test Doc    ${TESTNAME}    New doc
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test documentation to:\nNew doc

Append to test documentation
    ${tc} =    Check Test Doc    ${TESTNAME}     Original doc is continued \n\ntwice!
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test documentation to:\nOriginal doc is continued
    Check Log Message    ${tc.kws[2].msgs[0]}    Set test documentation to:\nOriginal doc is continued \n\ntwice!

Set suite documentation
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Set suite documentation to:\nNew suite doc
    Check Test Case    ${TESTNAME} 2
    Should Start With    ${SUITE.suites[0].doc}    New suite doc

Append to suite documentation
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Set suite documentation to:\nNew suite doc is continued
    ${tc} =    Check Test Case    ${TESTNAME} 2
    Check Log Message    ${tc.kws[1].msgs[0]}    Set suite documentation to:\nNew suite doc is continued \n\ntwice!
    Should Be Equal    ${SUITE.suites[0].doc}    New suite doc is continued \n\ntwice!

Set init file suite docs
    Should Be Equal     ${SUITE.doc}    Init file doc. Concatenated in setup. Appended in test.
    Check Log Message    ${SUITE.setup.msgs[0]}    Set suite documentation to:\nInit file doc. Concatenated in setup.

Set top level suite documentation
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Set suite documentation to:\nInit file doc. Concatenated in setup. Appended in test.

