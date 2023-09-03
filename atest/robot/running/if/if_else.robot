*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/if_else.robot
Resource          atest_resource.robot

*** Test Cases ***
If passing
    Check Test Case    ${TESTNAME}

If failing
    Check Test Case    ${TESTNAME}

If not executed
    Check Test Case    ${TESTNAME}

If not executed failing
    Check Test Case    ${TESTNAME}

If else - if executed
    Check Test Case    ${TESTNAME}

If else - else executed
    Check Test Case    ${TESTNAME}

If else - if executed - failing
    Check Test Case    ${TESTNAME}

If else - else executed - failing
    Check Test Case    ${TESTNAME}

If passing in keyword
    Check Test Case    ${TESTNAME}

If passing in else keyword
    Check Test Case    ${TESTNAME}

If failing in keyword
    Check Test Case    ${TESTNAME}

If failing in else keyword
    Check Test Case    ${TESTNAME}

Expression evaluation time is included in elapsed time
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be True    ${tc.body[0].elapsedtime} >= 200
    Should Be True    ${tc.body[0].body[0].elapsedtime} >= 100
    Should Be True    ${tc.body[0].body[1].elapsedtime} >= 100
    Should Be True    ${tc.body[0].body[2].elapsedtime} < 1000
