*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/dynamic_library_python.robot
Resource        atest_resource.robot

*** Test Cases ***
Passing, Logging and Returning
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  Hi tellus

Failing
    Check Test Case  ${TESTNAME}

Global Dynamic Library
    Check Test Case  ${TESTNAME}

Non-ASCII keyword name works when Unicode
    Check Test Case  ${TESTNAME}

Non-ASCII keyword name works when UTF-8 bytes
    Check Test Case  ${TESTNAME}

Non-ASCII keyword name fails when other bytes
    Check Stderr Contains    Calling dynamic method 'get_keyword_names' failed: UnicodeDecodeError:
    Check Test Case  ${TESTNAME}

Run Keyword in Static Library
    [Documentation]  Verify that library having run_keyword method but no get_keyword_names method is not considered dynamic
    Check Test Case  ${TESTNAME}

Not Found Keyword
    Check Test Case  ${TESTNAME}

Dynamic libraries should work without argument specification
    ${tc}=    Check test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    print this
    Check Log Message    ${tc.kws[1].msgs[0]}    x: something, y: something else
    Check Log Message    ${tc.kws[2].msgs[0]}    x: something, y: 0

Dynamic libraries should match named arguments same way as with user keywords
    ${tc}=    Check Test Case  ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    x y=1 z=2

Embedded Keyword Arguments
    Check Test Case  ${TESTNAME}
