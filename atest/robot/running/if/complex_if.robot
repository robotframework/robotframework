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
   ${tc} =    Check test case    ${TEST NAME}
   Check log message     ${tc.teardown.msgs[0]}    Teardown was found and executed.

For loop inside if
   Check Test Case    ${TESTNAME}

For loop inside for loop
   Check Test Case    ${TESTNAME}

Direct Boolean condition
   Check Test Case    ${TESTNAME}

Direct Boolean condition false
   Check Test Case    ${TESTNAME}

Nesting insanity
   Check Test Case    ${TESTNAME}

Recursive If
   Check Test Case    ${TESTNAME}

If creating variable
   Check Test Case    ${TESTNAME}

If inside if
   Check Test Case    ${TESTNAME}

For loop if else early exit
   Check Test Case    ${TESTNAME}

For loop if else if early exit
   Check Test Case    ${TESTNAME}