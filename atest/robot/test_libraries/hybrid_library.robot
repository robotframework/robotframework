*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/hybrid_library.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

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
    Check Log Message  ${ERRORS.msgs[0]}  Adding keyword 'non_existing_kw' to library 'GetKeywordNamesLibrary' failed: AttributeError: *  WARN  pattern=yes

Named Keyword Is Not Method
    Check Test Case  ${TESTNAME}
    Check Log Message  ${ERRORS.msgs[1]}  Adding keyword 'this_is_not_keyword' to library 'GetKeywordNamesLibrary' failed: Not a method or function  WARN

