*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/hybrid_library.robot
Resource          atest_resource.robot

*** Test Cases ***
Passing, Logging And Returning
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello world

Failing
    Check Test Case    ${TESTNAME}

Keyword Implemented In Library Class Itself
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    No need for __getattr__ here!!

Non Existing Attribute
    Check Test Case    ${TESTNAME}
    Adding keyword failed    0    Non-existing attribute
    ...    Getting handler method failed:
    ...    AttributeError: *
    ...    pattern=True

Named Keyword Is Not Method
    Check Test Case    ${TESTNAME}
    Adding keyword failed    1    not_method_or_function
    ...    Not a method or function.

Unexpected error getting attribute
    Check Test Case    ${TESTNAME}
    Adding keyword failed    2    Unexpected error getting attribute
    ...    Getting handler method failed:
    ...    TypeError: Oooops!

Name Set Using 'robot_name' Attribute
    Check Test Case    ${TESTNAME}

Old Name Doesn't Work If Name Set Using 'robot_name'
    Check Test Case    ${TESTNAME}

'robot_name' Attribute Set To None
    Check Test Case    ${TESTNAME}

Embedded Keyword Arguments
    Check Test Case    ${TESTNAME}

Name starting with an underscore is OK
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc.body[0]}            GetKeywordNamesLibrary.Starting With Underscore Is Ok
    Check Log Message     ${tc.body[0].msgs[0]}    This is explicitly returned from 'get_keyword_names' anyway.

Invalid get_keyword_names
    Error in file    3    test_libraries/hybrid_library.robot    3
    ...    Getting keyword names from library 'InvalidKeywordNames' failed:
    ...    Calling dynamic method 'get_keyword_names' failed:
    ...    Return value must be a list of strings, got integer.

__init__ exposed as keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].kwname}    Init

*** Keywords ***
Adding keyword failed
    [Arguments]    ${index}    ${name}    @{error}    ${pattern}=False
    Error in library    GetKeywordNamesLibrary
    ...    Adding keyword '${name}' failed:
    ...    @{error}
    ...    pattern=${pattern}
    ...    index=${index}
