*** Settings ***
Suite Setup    Run Remote Tests    library_info.robot    libraryinfo.py
Resource       remote_resource.robot

*** Test Cases ***
Load large library
    Check Test Case    ${TESTNAME}

Arguments
    Check Test Case    ${TESTNAME}

Types
    Check Test Case    ${TESTNAME}

Documentation
    ${tc} =    Check Test Case    Types
    Should Be Equal    ${tc.body[0].doc}    Documentation for 'some_keyword'.
    Should Be Equal    ${tc.body[4].doc}    Documentation for 'keyword_42'.

Tags
    ${tc} =    Check Test Case    Types
    Should Be Equal As Strings    ${tc.body[0].tags}    [some_keyword, tag]
    Should Be Equal As Strings    ${tc.body[4].tags}    [keyword_42, tag]
