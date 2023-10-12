*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for/continue_for_loop.robot
Resource          atest_resource.robot

*** Test Cases ***
Simple Continue For Loop
    Test And All Keywords Should Have Passed    allow not run=True

Continue For Loop In `Run Keyword`
    Test And All Keywords Should Have Passed    allow not run=True

Continue For Loop is not supported in user keyword
    Check Test Case    ${TESTNAME}

Continue For Loop Should Terminate Immediate Loop Only
    Test And All Keywords Should Have Passed    allow not run=True

Continue For Loop In User Keyword Should Terminate Immediate Loop Only
    Test And All Keywords Should Have Passed    allow not run=True

Continue For Loop Without For Loop Should Fail
    Check Test Case    ${TESTNAME}

Continue For Loop In User Keyword Without For Loop Should Fail
    Check Test Case    ${TESTNAME}

Continue For Loop Keyword Should Log Info
    ${tc} =    Check Test Case    Simple Continue For Loop
    Should Be Equal    ${tc.kws[0].kws[0].kws[0].full_name}    BuiltIn.Continue For Loop
    Check Log Message   ${tc.kws[0].kws[0].kws[0].msgs[0]}   Continuing for loop from the next iteration.

Continue For Loop In Test Teardown
    Test And All Keywords Should Have Passed

Continue For Loop In Keyword Teardown
    Test And All Keywords Should Have Passed

Invalid Continue For Loop In User Keyword Teardown
    Check Test Case    ${TESTNAME}

Continue For Loop If True
    Check Test Case    ${TESTNAME}

Continue For Loop If False
    Check Test Case    ${TESTNAME}

With Continuable Failure After
    Check Test Case    ${TESTNAME}

With Continuable Failure Before
    Check Test Case    ${TESTNAME}

With Continuable Failure In User Keyword
    Check Test Case    ${TESTNAME}
