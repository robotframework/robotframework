*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/fail.robot
Resource         atest_resource.robot

*** Test Cases ***
Fail
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2
    Length Should Be    ${tc.kws[0].msgs}    1

Fail with message
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2
    Length Should Be    ${tc.kws[0].msgs}    1

Fail with non-string message
    Check Test Case    ${TESTNAME}

Fail with non-true message having non-empty string representation
    Check Test Case    ${TESTNAME}

Set one tag
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag
    Length Should Be    ${tc.kws[0].msgs}    2
    Check Log Message    ${tc.kws[0].msgs[0]}     Set tag 'tag'.

Set multiple tags
    ${tc}=    Check Test Tags    ${TESTNAME}    force1    force2    tag1    tag2
    Length Should Be    ${tc.kws[0].msgs}    2
    Check Log Message    ${tc.kws[0].msgs[0]}     Set tags 'tag1' and 'tag2'.

Remove one tag
    ${tc}=    Check Test Tags    ${TESTNAME}    force2
    Length Should Be    ${tc.kws[0].msgs}    2
    Check Log Message    ${tc.kws[0].msgs[0]}      Removed tag 'force1'.

Remove multiple tags
    ${tc}=    Check Test Tags    ${TESTNAME}
    Length Should Be    ${tc.kws[0].msgs}    2
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tags 'force1' and 'force2'.

Remove multiple tags with pattern
    ${tc}=    Check Test Tags    ${TESTNAME}
    Length Should Be    ${tc.kws[0].msgs}    2
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'force?'.

Set and remove tags
    ${tc}=    Check Test Tags    ${TESTNAME}    force2    tag1    tag2
    Length Should Be    ${tc.kws[0].msgs}    3
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tags 'force1' and 'nonEx'.
    Check Log Message    ${tc.kws[0].msgs[1]}     Set tags 'tag1' and 'tag2'.

Set tags should not be removed
    ${tc}=    Check Test Tags    ${TESTNAME}    fii    foo
    Length Should Be    ${tc.kws[0].msgs}    3
    Check Log Message    ${tc.kws[0].msgs[0]}     Removed tag 'f*'.
    Check Log Message    ${tc.kws[0].msgs[1]}     Set tags 'foo' and 'fii'.
