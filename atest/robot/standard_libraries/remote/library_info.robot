*** Settings ***
Suite Setup    Run Remote Tests And Libdoc
Resource       remote_resource.robot

*** Test Cases ***
Load large library
    Check Test Case    ${TESTNAME}

Arguments
    Check Test Case    ${TESTNAME}
    Keyword Arguments Should Be    0    arg: int = None
    Keyword Arguments Should Be    -1    arg: bool    *extra

Types
    Check Test Case    ${TESTNAME}

Documentation
    ${tc} =    Check Test Case    Types
    Should Be Equal    ${tc.body[0].doc}    Documentation for 'some_keyword'.
    Should Be Equal    ${tc.body[4].doc}    Documentation for 'keyword_42'.

Tags
    ${tc} =    Check Test Case    Types
    Should Be Equal As Strings    ${tc.body[0].tags}    [tag]
    Should Be Equal As Strings    ${tc.body[4].tags}    [tag]

__intro__ is not exposed
    Check Test Case    ${TESTNAME}

__init__ is not exposed
    Check Test Case    ${TESTNAME}

Intro documentation
    Doc Should Be    __intro__ documentation.

Init documentation
    Init Doc Should Be     0    __init__ documentation.

*** Keywords ***
Run Remote Tests And Libdoc
    ${port} =    Run Remote Tests    library_info.robot    libraryinfo.py    stop server=no
    Should Be Empty    ${ERRORS}
    Run Libdoc And Parse Output    Remote::http://127.0.0.1:${port}
    [Teardown]      Run Keywords
    ...    Stop Remote Server    libraryinfo.py    AND
    ...    Remove Output Files
