*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/continue_on_failure_tag.robot
Resource          atest_resource.robot

*** Test Cases ***
Continue in test with tag
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[2].msgs[0]}    This should be executed

Continue in test with negative tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in test with negative tag and continuable error
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in user kewyord with tag
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    This should be executed

Continue in nested user kewyord with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in test with tag and user-kw without tag
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    This should be executed

Continue in test with tag and nested UK with and without tag
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}           This should be executed
    Check Log Message    ${tc.kws[0].kws[2].msgs[0]}    Continued on failure

Continue in for loop with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in for loop without tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in for loop in UK with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in for loop in UK without tag
    ${tc}=    Check Test Case    ${TESTNAME}
