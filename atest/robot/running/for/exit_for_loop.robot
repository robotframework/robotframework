*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for/exit_for_loop.robot
Resource          atest_resource.robot

*** Test Cases ***
Simple Exit For Loop
    Test And All Keywords Should Have Passed    allow not run=True

Exit For Loop In `Run Keyword`
    Test And All Keywords Should Have Passed    allow not run=True

Exit For Loop is not supported in user keyword
    Check Test Case    ${TESTNAME}

Exit For Loop In User Keyword With Loop
    Test And All Keywords Should Have Passed    allow not run=True

Exit For Loop In User Keyword With Loop Within Loop
    Test And All Keywords Should Have Passed    allow not run=True

Exit For Loop In User Keyword Calling User Keyword With Exit For Loop
    Check Test Case    ${TESTNAME}

Exit For Loop Without For Loop Should Fail
    Check Test Case    ${TESTNAME}

Exit For Loop In User Keyword Without For Loop Should Fail
    Check Test Case    ${TESTNAME}

Exit For Loop Keyword Should Log Info
    ${tc} =    Check Test Case    Simple Exit For Loop
    Should Be Equal    ${tc.kws[0].kws[0].kws[0].full_name}    BuiltIn.Exit For Loop
    Check Log Message   ${tc.kws[0].kws[0].kws[0].msgs[0]}   Exiting for loop altogether.

Exit For Loop In Test Teardown
    Test And All Keywords Should Have Passed

Exit For Loop In Keyword Teardown
    Test And All Keywords Should Have Passed

Invalid Exit For Loop In User Keyword Teardown
    Check Test Case    ${TESTNAME}

Exit For Loop If True
    Check Test Case    ${TESTNAME}

Exit For Loop If False
    Check Test Case    ${TESTNAME}

With Continuable Failure After
    Check Test Case    ${TESTNAME}

With Continuable Failure Before
    Check Test Case    ${TESTNAME}

With Continuable Failure In User Keyword
    Check Test Case    ${TESTNAME}
