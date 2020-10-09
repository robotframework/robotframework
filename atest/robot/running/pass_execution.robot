*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    running/pass_execution.robot
Resource         atest_resource.robot

*** Variables ***
${PREFIX}=       Execution passed with message:\n

*** Test Cases ***
Message is required
    Check Test Tags    ${TESTNAME}    force1    force2

With message
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2
    Check Log Message    ${tc.kws[0].msgs[0]}    ${PREFIX}My message

With HTML message
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2
    Check Log Message    ${tc.kws[0].msgs[0]}    ${PREFIX}<b>Message</b>    HTML

Empty message is not allowed
    Check Test Case    ${TESTNAME}

Only whitesapce message is not allowed
    Check Test Case    ${TESTNAME}

Used in user keyword
    Check Test Case    ${TESTNAME}

Used in nested user keyword
    Check Test Case    ${TESTNAME}

Used in library keyword raising `PassExecution` exception
    Check Test Case    ${TESTNAME}

Used in library keyword calling `BuiltIn.pass_execution()` method
    Check Test Case    ${TESTNAME}

Used in template keyword
    Check Test Case    ${TESTNAME}

Used in for loop
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    ${PREFIX}Message with 'foo'

Used in setup
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword Should Have Been Executed    ${tc.kws[0]}
    Keyword Should Have Been Executed    ${tc.teardown}

Used in teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.teardown.status}    PASS
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    ${PREFIX}This message is used.

Before failing teardown
    Check Test Case    ${TESTNAME}

After continuable failure
    Check Test Case    ${TESTNAME}

After continuable failure in user keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].status}    FAIL

After continuable failure in FOR loop
    ${tc}=    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].status}    FAIL
    Should Be Equal    ${tc.kws[0].kws[0].status}    FAIL
    Should Be Equal    ${tc.kws[0].kws[0].kws[0].status}    FAIL
    Should Be Equal    ${tc.kws[0].kws[0].kws[1].status}    PASS

After continuable failure and before failing teardown
    Check Test Case    ${TESTNAME}

After continuable failure in setup
    Check Test Case    ${TESTNAME}

After continuable failure in teardown
    Check Test Case    ${TESTNAME}

After continuable failure in nested user keyword
    Check Test Case    ${TESTNAME}

After continuable failure in keyword teardown
    Check Test Case    ${TESTNAME}

Remove one tag
    ${tc}=    Check Test Tags    ${TESTNAME}    force2
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'force1'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}Message

Remove multiple tags
    ${tc}=    Check Test Tags    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tags 'force1' and 'force2'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}Message

Remove tags with pattern
    ${tc}=    Check Test Tags    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'force?'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}Message

Set one tag
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag
    Check Log Message    ${tc.kws[0].msgs[0]}     Set tag 'tag'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}Message

Set multiple tags
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag1    tag2
    Check Log Message    ${tc.kws[0].msgs[0]}     Set tags 'tag1' and 'tag2'.
    Check Log Message    ${tc.kws[0].msgs[1]}     ${PREFIX}Message

Set and remove tags
    ${tc}=    Check Test Tags    ${TESTNAME}    tag1    tag2
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'force?'.
    Check Log Message    ${tc.kws[0].msgs[1]}     Set tags 'tag1' and 'tag2'.
    Check Log Message    ${tc.kws[0].msgs[2]}     ${PREFIX}Message

Set tags are not removed
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag1    tag2
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'tag?'.
    Check Log Message    ${tc.kws[0].msgs[1]}     Set tags 'tag1' and 'tag2'.
    Check Log Message    ${tc.kws[0].msgs[2]}     ${PREFIX}Message

Set tags in teardown
    ${tc}=    Check Test Tags    ${TESTNAME}    tag1    tag2
    Check Log Message    ${tc.teardown.msgs[0]}    Removed tag 'force?'.
    Check Log Message    ${tc.teardown.msgs[1]}    Set tags 'tag1' and 'tag2'.
    Check Log Message    ${tc.teardown.msgs[2]}    ${PREFIX}Message

Pass Execution If when condition is true
    Check Test Case    ${TESTNAME}

Pass Execution If when condition is false
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword Should Have Been Executed    ${tc.kws[1]}

Pass Execution If resolves variables only condition is true
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword Should Have Been Executed    ${tc.kws[1]}

Pass Execution If with multiple variables
    Check Test Tags    ${TESTNAME}    force1    force2    my    tags

Statuses should be correct when running tests
    Stdout Should Contain    SEPARATOR=\n
    ...    34 tests, 20 passed, 14 failed

Passes suite setup and teardown and can modify tags in former
    Run Tests    ${EMPTY}    running/pass_execution_in_suite_setup_and_teardown.robot
    Check Test Tags    Test in suite with valid Pass Execution usage in Suite Setup and Teardown
    ...    force1    tag1    tag2

Trying to modify tags in suite teardown fails
    Run Tests    ${EMPTY}    running/pass_execution_in_suite_teardown_invalid.robot
    Check Test Tags    Test in suite with invalid Pass Execution usage in Suite Teardown
    ...    force1    force2

*** Keywords ***
Keyword Should Have Been Executed
    [Arguments]    ${kw}
    Should Be Equal    ${kw.name}    Should Be Executed
