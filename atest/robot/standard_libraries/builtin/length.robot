*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/length.robot
Resource          builtin_resource.robot

*** Test Cases ***
Get Length
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Length is 0
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Length is 1
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    Length is 2
    Check Log Message    ${tc.kws[3].kws[0].msgs[0]}    Length is 3
    Check Log Message    ${tc.kws[4].kws[0].msgs[0]}    Length is 11
    Check Log Message    ${tc.kws[5].kws[0].msgs[0]}    Length is 0

Length Should Be
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[-1].msgs[0]}    Length is 2
    Check Log Message    ${tc.kws[-1].msgs[1]}    Length of '*' should be 3 but is 2.    FAIL    pattern=yep
    Check Log Message    ${tc.kws[-1].msgs[2]}    Traceback*    DEBUG    pattern=yep
    Length Should Be    ${tc.kws[-1].msgs}    3

Length Should Be with custom message
    Check Test Case    ${TESTNAME}

Length Should Be with invalid length
    Check Test Case    ${TESTNAME}

Should Be Empty
    Check test case    ${TESTNAME} 1
    Check test case    ${TESTNAME} 2
    Check test case    ${TESTNAME} 3

Should Be Empty with custom message
    Check test case    ${TESTNAME}

Should Not Be Empty
    Check test case    ${TESTNAME} 1
    Check test case    ${TESTNAME} 2

Should Not Be Empty with custom message
    Check test case    ${TESTNAME}

Getting length with `length` method
    Check test case    ${TESTNAME}

Getting length with `size` method
    Check test case    ${TESTNAME}

Getting length with `length` attribute
    Check test case    ${TESTNAME}
