*** Settings ***
Documentation     Tests for return values from keywords. Tests include e.g.
...               setting different return values for variables and checking
...               messages that are automatically logged when variables are set.
...               See also return_values.robot
Suite Setup       Run Tests    ${EMPTY}    variables/return_values_java.robot
Force Tags        regression    jybot
Resource          atest_resource.robot

*** Test Cases ***
Set Multiple Scalar Variables Using Array
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${var1}, \${var2} = ExampleJavaLibrary.Get String Array
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var1} = first value
    Check Log Message    ${tc.kws[0].msgs[1]}    \${var2} = second value
    Should Be Equal    ${tc.kws[3].name}    \${i1}, \${i2}, \${i42} = ExampleJavaLibrary.Get Array Of Three Ints
    Check Log Message    ${tc.kws[3].msgs[0]}    \${i1} = 1
    Check Log Message    ${tc.kws[3].msgs[1]}    \${i2} = 2
    Check Log Message    ${tc.kws[3].msgs[2]}    \${i42} = 42

Set Object To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = This is my name in Java

Set List Variable Using Array
    ${tc} =    Check Test Case    ${TEST NAME}
    Verify List Variable Assigment    ${tc}    Get String Array
    Should Be Equal    ${tc.kws[3].name}    \@{listvar} = ExampleJavaLibrary.Get Array Of Three Ints
    Check Log Message    ${tc.kws[3].msgs[0]}    \@{listvar} = [ 1 | 2 | 42 ]

Set List Variable Using Vector
    ${tc} =    Check Test Case    ${TEST NAME}
    Verify List Variable Assigment    ${tc}    Get String Vector

Set List Variable Using ArrayList
    ${tc} =    Check Test Case    ${TEST NAME}
    Verify List Variable Assigment    ${tc}    Get String Array List

Set List Variable Using String List
    ${tc} =    Check Test Case    ${TEST NAME}
    Verify List Variable Assigment    ${tc}    Get String List

Set List Variable Using String Iterator
    ${tc} =    Check Test Case    ${TEST NAME}
    Verify List Variable Assigment    ${tc}    Get String Iterator

Set Scalar Variables With More Values Than Variables Using Array
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${a} = a
    Check Log Message    ${tc.kws[0].msgs[1]}    \${b} = b
    Check Log Message    ${tc.kws[0].msgs[2]}    \${c} = [u'c', u'd', u'e', u'f']
    Check Log Message    ${tc.kws[4].msgs[0]}    \${i1} = 1
    Check Log Message    ${tc.kws[4].msgs[1]}    \${i2&42} = [2, 42]

Set Multiple Scalars With Too Few Values Using Array
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Cannot assign return values: Need more values than 3.    FAIL

Set List To Scalar And List Variables Using Array
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${a}, \${b}, \@{c} = ExampleJavaLibrary.Get Array Of Three Ints
    Check Log Message    ${tc.kws[0].msgs[0]}    \${a} = 1
    Check Log Message    ${tc.kws[0].msgs[1]}    \${b} = 2
    Check Log Message    ${tc.kws[0].msgs[2]}    \@{c} = [ 42 ]

Return Unrepresentable Object
    [Documentation]    See http://code.google.com/p/robotframework/issues/detail?id=967
    Check Test Case    ${TEST NAME}

*** Keywords ***
Verify List Variable Assigment
    [Arguments]    ${tc}    ${kw name}
    Should Be Equal    ${tc.kws[0].name}    \@{listvar} = ExampleJavaLibrary.${kw name}
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{listvar} = [ v1 | v2 | v3 ]
