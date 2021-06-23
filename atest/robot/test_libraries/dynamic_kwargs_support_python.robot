*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/dynamic_kwargs_support_python.robot
Resource          atest_resource.robot

*** Test Cases ***
Dynamic kwargs support should work without argument specification
    ${tc}=    Check test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    print this
    Check Log Message    ${tc.kws[1].msgs[0]}    x: something, y: something else
    Check Log Message    ${tc.kws[2].msgs[0]}    x: something, y: 0
    Check Log Message    ${tc.kws[3].msgs[0]}    x 1 3
    Check Log Message    ${tc.kws[4].msgs[0]}    something 13 3 y:12

Unexpected keyword argument
    Check test Case    ${TESTNAME}

Documentation and Argument Boundaries Work With Kwargs
    Check test case and its keywords  Kwargs
    ...    key:value

Documentation and Argument Boundaries Work With Varargs and Kwargs
    Check test case and its keywords  Varargs and Kwargs
    ...    \
    ...    1 2 3
    ...    key:value
    ...    1 2 3 key:value

Documentation and Argument Boundaries Work When Argspec is None
    Check test case and its keywords  No Arg Spec
    ...    \
    ...    1 2 3
    ...    key:value
    ...    1 2 3 key:value

*** Keywords ***
Check test case and its keywords
    [Arguments]    ${keyword}    @{argstrings}
    ${tc} =    Check Test case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].doc}    Keyword documentation for ${keyword}
    FOR    ${index}    ${argstr}    IN ENUMERATE   @{argstrings}
        Check Log Message    ${tc.kws[${index}].msgs[0]}    Executed keyword ${keyword} with arguments ${argstr}
    END
