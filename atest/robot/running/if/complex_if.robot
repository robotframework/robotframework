*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/complex_if.robot
Resource          atest_resource.robot

*** Test Cases ***
Multiple keywords in if
    Check Test Case    ${TESTNAME}

Nested ifs
    Check Test Case    ${TESTNAME}

If inside for loop
    Check Test Case    ${TESTNAME}

Setting after if
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown.msgs[0]}    Teardown was found and executed.

For loop inside if
    Check Test Case    ${TESTNAME}

For loop inside for loop
    Check Test Case    ${TESTNAME}

Direct Boolean condition
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].status}                    PASS
    Should Be Equal    ${tc.body[0].body[0].status}            PASS
    Should Be Equal    ${tc.body[0].body[0].body[0].status}    PASS

Direct Boolean condition false
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].status}                     PASS
    Should Be Equal    ${tc.body[0].body[0].status}            NOT RUN
    Should Be Equal    ${tc.body[0].body[0].body[0].status}    NOT RUN

Nesting insanity
    Check Test Case    ${TESTNAME}

Recursive If
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].kws[0].status}                  PASS
    Should Be Equal    ${tc.kws[0].kws[0].kws[0].kws[0].status}    PASS

If creating variable
    Check Test Case    ${TESTNAME}

If inside if
    Check Test Case    ${TESTNAME}

For loop if else early exit
    Check Test Case    ${TESTNAME}

For loop if else if early exit
    Check Test Case    ${TESTNAME}

If with comments
    Check Test Case    ${TESTNAME}

If with invalid condition after valid is ok
    Check Test Case    ${TESTNAME}

If with dollar var from variables table
    Check Test Case    ${TESTNAME}
