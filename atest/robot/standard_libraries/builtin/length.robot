*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/length.robot
Resource          builtin_resource.robot

*** Test Cases ***
Get Length
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0]}    Length is 0.
    Check Log Message    ${tc[1, 0, 0]}    Length is 1.
    Check Log Message    ${tc[2, 0, 0]}    Length is 2.
    Check Log Message    ${tc[3, 0, 0]}    Length is 3.
    Check Log Message    ${tc[4, 0, 0]}    Length is 11.
    Check Log Message    ${tc[5, 0, 0]}    Length is 0.

Length Should Be
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[-1, 0]}      Length is 2.
    Check Log Message    ${tc[-1, 1]}      Length of '*' should be 3 but is 2.    FAIL    pattern=yep
    Check Log Message    ${tc[-1, 2]}      Traceback*    DEBUG    pattern=yep
    Length Should Be     ${tc[-1].body}    3

Length Should Be with custom message
    Check Test Case    ${TESTNAME}

Length Should Be with invalid length
    Check Test Case    ${TESTNAME}

Should Be Empty
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Should Be Empty with custom message
    Check Test Case    ${TESTNAME}

Should Not Be Empty
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Should Not Be Empty with custom message
    Check Test Case    ${TESTNAME}

Getting length with `length` method
    Check Test Case    ${TESTNAME}

Getting length with `size` method
    Check Test Case    ${TESTNAME}

Getting length with `length` attribute
    Check Test Case    ${TESTNAME}
