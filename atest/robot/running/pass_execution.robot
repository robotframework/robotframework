*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    running/pass_execution.robot
Resource         atest_resource.robot

*** Variables ***
${PREFIX}=    Execution passed with message:\n

*** Test Cases ***
Message is required
    Check Test Tags    ${TESTNAME}    force1    force2

With message
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2
    Check Log Message    ${tc.kws[0].msgs[0]}    ${PREFIX}exception message

With HTML message
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2
    Check Log Message    ${tc.kws[0].msgs[0]}    ${PREFIX}<b>message</b>    HTML

With empty string as a message
    Check Test Case    ${TESTNAME}

With only whitespace as a message
    Check Test Case    ${TESTNAME}

Remove one tag
    ${tc}=    Check Test Tags    ${TESTNAME}    force2
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'force1'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}message

Remove multiple tags
    ${tc}=    Check Test Tags    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tags 'force1' and 'force2'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}message

Remove tags with pattern
    ${tc}=    Check Test Tags    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'force?'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}message

Set one tag
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag
    Check Log Message    ${tc.kws[0].msgs[0]}     Set tag 'tag'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}message

Set multiple tags
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag1    tag2
    Check Log Message    ${tc.kws[0].msgs[0]}     Set tags 'tag1' and 'tag2'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}message

Set and remove tags
    ${tc}=    Check Test Tags    ${TESTNAME}    tag1    tag2
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'force?'.
    Check Log Message    ${tc.kws[0].msgs[1]}     Set tags 'tag1' and 'tag2'.
    Check Log Message    ${tc.kws[0].msgs[2]}     ${PREFIX}message

Set tags are not removed
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag1    tag2
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'tag?'.
    Check Log Message    ${tc.kws[0].msgs[1]}     Set tags 'tag1' and 'tag2'.
    Check Log Message    ${tc.kws[0].msgs[2]}     ${PREFIX}message

With template
    Check Test Case    ${TESTNAME}

Inside user keyword
    Check Test Case    ${TESTNAME}

Inside nested user keyword
    Check Test Case    ${TESTNAME}

With continuable failure
    Check Test Case    ${TESTNAME}

With continuable failure in user keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].status}    FAIL

With continuable failure in FOR loop
    ${tc}=    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].status}    FAIL
    Should Be Equal    ${tc.kws[0].kws[0].status}    FAIL
    Should Be Equal    ${tc.kws[0].kws[0].kws[0].status}    FAIL
    Should Be Equal    ${tc.kws[0].kws[0].kws[1].status}    PASS

With continuable failure and test case teardown fails
    ${tc}=    Check Test Case    ${TESTNAME}

With test case setup
    ${tc}=    Check Test Tags    ${TESTNAME}    force2    tag
    Should Be Equal    ${tc.setup.status}    PASS
    Check Log Message    ${tc.setup.msgs[0]}    Removed tag 'force1'.
    Check Log Message    ${tc.setup.msgs[1]}    Set tag 'tag'.
    Check Log Message    ${tc.setup.msgs[2]}    ${PREFIX}message

If test case setup fails
    ${tc}=    Check Test Case    ${TESTNAME}

With test case teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.teardown.status}    PASS
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    ${PREFIX}This message is used.

If test case teardown fails
    Check Test Case    ${TESTNAME}

Modifying tags in test case teardown should succeed
    ${tc}=    Check Test Tags    ${TESTNAME}    tag1    tag2
    Check Log Message    ${tc.teardown.msgs[0]}    Removed tag 'force?'.
    Check Log Message    ${tc.teardown.msgs[1]}    Set tags 'tag1' and 'tag2'.
    Check Log Message    ${tc.teardown.msgs[2]}    ${PREFIX}message

With for loop
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    Set tag 'tag'.
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[1]}    ${PREFIX}message

With library throwing exception
    Check Test Case    ${TESTNAME}

With library calling Pass Execution keyword
    Check Test Case    ${TESTNAME}

Should pass execution if condition true
    Check Test Case    ${TESTNAME}

Should not pass execution if condition false
    Check Test Case    ${TESTNAME}

Should not resolve variables if condition false
    Check Test Case    ${TESTNAME}

Should fail if non-existing variable if condition true
    Check Test Case    ${TESTNAME}

With multiple variables
    Check Test Tags    ${TESTNAME}    force1    force2    my tag

With continuable failure in test setup
    Check Test Case    ${TESTNAME}

With continuable failure in test teardown
    Check Test Case    ${TESTNAME}

With continuable failure in keyword teardown
    Check Test Case    ${TESTNAME}

Statuses should be correct when running tests
    Check Stdout Contains    SEPARATOR=\n
    ...    35 critical tests, 18 passed, 17 failed
    ...    35 tests total, 18 passed, 17 failed

Passes suite setup and teardown and can modify tags in former
    Run Tests    ${EMPTY}    running/pass_execution_in_suite_setup_and_teardown.robot
    Check Test Tags    Test in suite with valid Pass Execution usage in Suite Setup and Teardown
    ...    force1    tag1    tag2

Trying to modify tags in suite teardown fails
    Run Tests    ${EMPTY}    running/pass_execution_in_suite_teardown_invalid.robot
    Check Test Tags    Test in suite with invalid Pass Execution usage in Suite Teardown
    ...    force1    force2
