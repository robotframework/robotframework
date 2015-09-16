*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/hybrid_library.robot
Resource        atest_resource.robot

*** Test Cases ***
Passing, Logging And Returning
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  Hello world

Failing
    Check Test Case  ${TESTNAME}

Keyword Implemented In Library Class Itself
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  No need for __getattr__ here!!

Non Existing Keyword
    Check Test Case  ${TESTNAME}
    Check Log Message  ${ERRORS.msgs[0]}  Adding keyword 'non_existing_kw' to library 'GetKeywordNamesLibrary' failed: AttributeError: *  ERROR  pattern=yes

Named Keyword Is Not Method
    Check Test Case  ${TESTNAME}
    Check Log Message  ${ERRORS.msgs[1]}  Adding keyword 'this_is_not_keyword' to library 'GetKeywordNamesLibrary' failed: Not a method or function  ERROR

Name Set Using 'robot_name' Attribute
    Check Test Case  ${TESTNAME}

Old Name Doesn't Work If Name Set Using 'robot_name'
    Check Test Case  ${TESTNAME}

'robot_name' Attribute Set To None
    Check Test Case  ${TESTNAME}

Embedded Keyword Arguments
    Check Test Case  ${TESTNAME}
