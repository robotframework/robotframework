*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  running/errors_in_test_teardown.robot
Resource        atest_resource.robot

*** Test Cases ***
One Error In Teardown
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.teardown.kws[1].msgs[0]}  This Should Be executed

Many Errors In Teardown
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.teardown.kws[2].msgs[0]}  This Should Also Be Executed

Errors In Teardown When Setting Variables
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.teardown.kws[0].msgs[0]}  no return value is set  FAIL
    Check Log Message  ${tc.teardown.kws[0].msgs[1]}  \${ret} = None

Errors In For Loop In Teardown
    Check Test Case  ${TESTNAME}

Keyword Timeout In Teardown
    ${tc} =  Check Test Case  ${TESTNAME}
    Length Should Be  ${tc.teardown.kws}  1

Syntax Error in Teardown
    ${tc} =  Check Test Case  ${TESTNAME}
    Length Should Be  ${tc.teardown.kws}  3

Syntax Error in For Loop in Teardown
    ${tc} =  Check Test Case  ${TESTNAME}
    Length Should Be  ${tc.teardown.kws}  2

Fatal Error In Teardown
    ${tc} =  Check Test Case  ${TESTNAME}
    Length Should Be  ${tc.teardown.kws}  1

Suite Teardown Is Executed Fully
    ${ts} =  Get Test Suite  errors in test teardown
    Check Log Message  ${ts.teardown.kws[0].msgs[0]}  Suite Message 1  FAIL
    Check Log Message  ${ts.teardown.kws[1].msgs[0]}  Suite Message 2 (with ∏ön ÄßÇïï €§)  FAIL
    Check Log Message  ${ts.teardown.kws[2].msgs[0]}  No keyword with name 'Missing Keyword' found.  FAIL
    Check Log Message  ${ts.teardown.kws[3].msgs[0]}  This As Well Should Be Executed
    ${msg} =  Catenate  SEPARATOR=\n
    ...  Suite teardown failed:
    ...  Several failures occurred:\n
    ...  1) Suite Message 1\n
    ...  2) Suite Message 2 (with ∏ön ÄßÇïï €§)\n
    ...  3) No keyword with name 'Missing Keyword' found.
    Should Be Equal  ${ts.message}  ${msg}

Suite Teardown Should Stop At Fatal Error
    Run Tests  ${EMPTY}  running/fatal_error_in_suite_teardown.robot
    ${ts} =  Get Test Suite  fatal error in suite teardown
    Length Should Be   ${ts.teardown.kws}   1
