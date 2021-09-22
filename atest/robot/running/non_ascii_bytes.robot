*** Settings ***
Documentation     These tests log, raise, and return messages containing non-ASCII byte strings.
...               When these messages are logged, the bytes are escaped.
Suite Setup       Run Tests    ${EMPTY}    running/non_ascii_bytes.robot
Resource          atest_resource.robot
Variables         ${DATADIR}/running/expbytevalues.py

*** Test Cases ***
In Message
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    ${exp_log_msg}

In Multiline Message
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    ${exp_log_multiline_msg}

In Return Value
    [Documentation]    Return value is not altered by the framework and thus it
    ...    contains the exact same bytes that the keyword returned.
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${retval} = ${exp_return_msg}

In Exception
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    ${exp_error_msg}    FAIL

In Exception In Setup
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.setup.msgs[0]}    ${exp_error_msg}    FAIL

In Exception In Teardown
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown.msgs[0]}    ${exp_error_msg}    FAIL
