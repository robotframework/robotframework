*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/wait_until_keyword_succeeds.robot
Resource         atest_resource.robot

*** Test Cases ***
Fail Because Timeout exceeded
    ${tc} =    Check Test Case    ${TESTNAME}
    # Cannot test exactly how many times kw is run because it depends on interpreter speed.
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Still 2 times to fail!    FAIL
    Should Be True    len($tc.kws[0].kws) < 4

Pass with first Try
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Used to test that variable name, not value, is shown in arguments
    Length Should Be    ${tc.kws[0].kws}    1

Pass With Some Medium Try
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Still 2 times to fail!    FAIL
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    Still 1 times to fail!    FAIL
    Check Log Message    ${tc.kws[0].kws[2].msgs[0]}    Still 0 times to fail!    FAIL
    Length Should Be    ${tc.kws[0].kws}    4

Pass With Last Possible Try
    Check Test Case    ${TESTNAME}

Pass With Returning Value Correctly
    Check Test Case    ${TESTNAME}

Invalid Timeout Does Not Cause Uncatchable Failure
    Check Test Case    ${TESTNAME}

Invalid Retry Interval Does Not Cause Uncatchable Failure
    Check Test Case    ${TESTNAME}

Wait Until In User Keyword
    Check Test Case    ${TESTNAME}

Failing User Keyword with Wait Until
    Check Test Case    ${TESTNAME}

Passing User Keyword with Wait Until
    Check Test Case    ${TESTNAME}

Wait Until With Longer Test Timeout
    Check Test Case    ${TESTNAME}

Wait Until With Shorter Test Timeout
    Check Test Case    ${TESTNAME}

Wait Until With Longer Keyword Timeout
    Check Test Case    ${TESTNAME}

Wait Until With Shorter Keyword Timeout
    Check Test Case    ${TESTNAME}

Retry as count
    Check Test Case    ${TESTNAME}

Retry as count failing
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Retry count must be integer
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Retry count must be positive
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

No retry after syntax error
    Check Test Case    ${TESTNAME}

No retry if keyword name is not string
    Check Test Case    ${TESTNAME}

Retry if keyword is not found
    Check Test Case    ${TESTNAME}

Retry if wrong number of arguments
    Check Test Case    ${TESTNAME}

Retry if variable is not found
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    Variable '\${nonexisting}' not found.    FAIL
    Check Log Message    ${tc.kws[0].kws[1].kws[0].msgs[0]}    Variable '\${nonexisting}' not found.    FAIL
    Check Log Message    ${tc.kws[0].kws[2].kws[0].msgs[0]}    Variable '\${nonexisting}' not found.    FAIL
    Length Should Be    ${tc.kws[0].kws}    3

Pass With Initially Nonexisting Variable Inside Wait Until Keyword Succeeds
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    Variable '\${created after accessing first time}' not found.    FAIL
    Check Log Message    ${tc.kws[0].kws[1].kws[0].msgs[0]}    created in keyword teardown
    Length Should Be    ${tc.kws[0].kws}    2

Variable Values Should Not Be Visible In Keyword Arguments
    ${tc} =    Check Test Case    Pass With First Try
    Check Keyword Data    ${tc.kws[0].kws[0]}    BuiltIn.Log    args=\${HELLO}

Strict retry interval
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.body[0].kws}    4
    Elapsed Time Should Be Valid    ${tc.body[0].elapsed_time}    minimum=0.3    maximum=0.9

Fail with strict retry interval
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.body[0].kws}    3
    Elapsed Time Should Be Valid    ${tc.body[0].elapsed_time}    minimum=0.2    maximum=0.6

Strict retry interval violation
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.body[0].kws}    4
    Elapsed Time Should Be Valid    ${tc.body[0].elapsed_time}    minimum=0.4    maximum=1.2
    FOR    ${index}    IN    1    3    5    7
        Check Log Message    ${tc.body[0].body[${index}]}
        ...    Keyword execution time ??? milliseconds is longer than retry interval 100 milliseconds.
        ...    WARN    pattern=True
    END

Strict and invalid retry interval
    Check Test Case    ${TESTNAME}

Keyword name as variable
    Check Test Case    ${TESTNAME}
