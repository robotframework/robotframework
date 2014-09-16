*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/exit_for_loop.robot
Force Tags        regression
Default Tags      pybot    jybot
Resource          atest_resource.robot

*** Test Cases ***
Simple Exit For Loop
    Test And All Keywords Should Have Passed

Exit For Loop In `Run Keyword`
    Test And All Keywords Should Have Passed

Exit For Loop In User Keyword
    Test And All Keywords Should Have Passed

Exit For Loop In User Keyword With Loop
    Test And All Keywords Should Have Passed

Exit For Loop In User Keyword With Loop Within Loop
    Test And All Keywords Should Have Passed

Exit For Loop In User Keyword Calling User Keyword With Exit For Loop
    Test And All Keywords Should Have Passed

Exit For Loop Without For Loop Should Fail
    Check Test Case    ${TESTNAME}

Exit For Loop In User Keyword Without For Loop Should Fail
    Check Test Case    ${TESTNAME}

Exit For Loop Keyword Should Log Info
    ${tc} =    Check Test Case    Simple Exit For Loop
    Should Be Equal    ${tc.kws[0].kws[0].kws[0].name}    BuiltIn.Exit For Loop
    Check Log Message   ${tc.kws[0].kws[0].kws[0].msgs[0]}   Exiting for loop altogether.

Custom Exception with ROBOT_EXIT_FOR_LOOP Works But Is Deprecated
    ${msg} =    Catenate
    ...    Support for using 'ROBOT_EXIT_FOR_LOOP' attribute to exit for loops
    ...    is deprecated in Robot Framework 2.8 and will be removed in 2.9.
    Check Log Message   ${ERRORS[0]}    ${msg}   WARN
    Test And All Keywords Should Have Passed

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
