*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_and_return.robot
Resource         atest_resource.robot

*** Test Cases ***
Return one value
    ${tc} =    Check Test Case    ${TESTNAME}
    Check log message    ${tc.kws[0].kws[0].msgs[0]}    Returning from the enclosing user keyword.

Return multiple values
    Check Test Case    ${TESTNAME}

Return nothing
    ${tc} =    Check Test Case    ${TESTNAME}
    Check log message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    No return value
    Check log message    ${tc.kws[0].kws[0].msgs[0]}    Returning from the enclosing user keyword.

Nested usage
    Check Test Case    ${TESTNAME}

Keyword fails
    Check Test Case    ${TESTNAME}

Inside Run Keyword variants
    ${tc} =    Check Test Case    ${TESTNAME}
    Check log message    ${tc.kws[2].kws[0].kws[0].msgs[0]}    First keyword
    Check log message    ${tc.kws[2].kws[0].kws[2].msgs[0]}    Returning from the enclosing user keyword.

Using Run Keyword variants
    ${tc} =    Check Test Case    ${TESTNAME}
    Check log message    ${tc.kws[2].kws[0].kws[0].kws[1].msgs[0]}    Second keyword
    Check log message    ${tc.kws[2].kws[0].kws[0].kws[2].msgs[0]}    Returning from the enclosing user keyword.

Outside user keyword
    Check Test Case    ${TESTNAME}

With list variable containing escaped items
    Check Test Case    ${TESTNAME}

Return strings that needs to be escaped
    Check Test Case    ${TESTNAME}

Run Keyword And Return If
    ${tc} =    Check Test Case    ${TESTNAME}
    Check log message    ${tc.kws[0].kws[1].msgs[0]}    Returning from the enclosing user keyword.
    Check log message    ${tc.kws[2].kws[1].msgs[0]}    Returning from the enclosing user keyword.
    Check log message    ${tc.kws[4].kws[0].kws[2].kws[0].msgs[0]}    Returning from the enclosing user keyword.

Run Keyword And Return If can have non-existing keywords and variables if condition is not true
    Check Test Case    ${TESTNAME}

Run Keyword And Return If with list variable containing escaped items
    Check Test Case    ${TESTNAME}

Run Keyword And Return If return strings that needs to be escaped
    Check Test Case    ${TESTNAME}

Run Keyword And Return In Teardown
    Check Test Case    ${TESTNAME}

Run Keyword And Return In Teardown When Keyword Fails
    Check Test Case    ${TESTNAME}
