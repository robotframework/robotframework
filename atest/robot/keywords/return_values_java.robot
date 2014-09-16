*** Settings ***
Documentation   Tests for return values from keywords. Tests include e.g. setting different return values for variables and checking messages that are automatically logged when variables are set. Setting different return values got from Java libraries are tested thoroughly in java_libraries.html.
Suite Setup     Run Tests  ${EMPTY}  keywords/return_values_java.robot
Force Tags      regression  jybot
Resource        atest_resource.robot

*** Test Cases ***
Set Multiple Scalar Variables Using Array
    ${test} =  Check Test Case  Set Multiple Scalar Variables Using Array
    Should Be Equal  ${test.kws[0].name}  \${var1}, \${var2} = ExampleJavaLibrary.Get String Array
    Check Log Message  ${test.kws[0].msgs[0]}  \${var1} = first value
    Check Log Message  ${test.kws[0].msgs[1]}  \${var2} = second value
    Should Be Equal  ${test.kws[3].name}  \${i1}, \${i2}, \${i42} = ExampleJavaLibrary.Get Array Of Three Ints
    Check Log Message  ${test.kws[3].msgs[0]}  \${i1} = 1
    Check Log Message  ${test.kws[3].msgs[1]}  \${i2} = 2
    Check Log Message  ${test.kws[3].msgs[2]}  \${i42} = 42

Set Object To Scalar Variable
    ${test} =  Check Test Case  Set Object to Scalar Variable
    Check Log Message  ${test.kws[0].msgs[0]}  \${var} = This is my name in Java

Set List Variable Using Array
    ${test} =  Check Test Case  Set List Variable Using Array
    Verify List Variable Assigment  ${test}  Get String Array
    Should Be Equal  ${test.kws[3].name}  \@{listvar} = ExampleJavaLibrary.Get Array Of Three Ints
    Check Log Message  ${test.kws[3].msgs[0]}  \@{listvar} = [ 1 | 2 | 42 ]

Set List Variable Using Vector
    ${test} =  Check Test Case  Set List Variable Using Vector
    Verify List Variable Assigment  ${test}  Get String Vector

Set List Variable Using ArrayList
    ${test} =  Check Test Case  Set List Variable Using Array List
    Verify List Variable Assigment  ${test}  Get String Array List

Set List Variable Using String List
    ${test} =  Check Test Case  Set List Variable Using String List
    Verify List Variable Assigment  ${test}  Get String List

Set List Variable Using String Iterator
    ${test} =  Check Test Case  Set List Variable Using String Iterator
    Verify List Variable Assigment  ${test}  Get String Iterator

Set Scalar Variables With More Values Than Variables Using Array
    ${test} =  Check Test Case  Set Scalar Variables With More Values Than Variables Using Array
    Check Log Message  ${test.kws[0].msgs[0]}  \${a} = a
    Check Log Message  ${test.kws[0].msgs[1]}  \${b} = b
    Check Log Message  ${test.kws[0].msgs[2]}  \${c} = [u'c', u'd', u'e', u'f']
    Check Log Message  ${test.kws[4].msgs[0]}  \${i1} = 1
    Check Log Message  ${test.kws[4].msgs[1]}  \${i2&42} = [2, 42]

Set Multiple Scalars With Too Few Values Using Array
    ${test} =  Check Test Case  Set Multiple Scalars with too few values Using Array
    Check Log Message  ${test.kws[0].msgs[0]}  Cannot assign return values: Need more values than 3.  FAIL

Set List To Scalar And List Variables Using Array
    ${test} =  Check Test Case  Set List to Scalar and list variables Using Array
    Should Be Equal  ${test.kws[0].name}  \${a}, \${b}, \@{c} = ExampleJavaLibrary.Get Array Of Three Ints
    Check Log Message  ${test.kws[0].msgs[0]}  \${a} = 1
    Check Log Message  ${test.kws[0].msgs[1]}  \${b} = 2
    Check Log Message  ${test.kws[0].msgs[2]}  \@{c} = [ 42 ]

Return Unrepresentable Object
  [Documentation]   See http://code.google.com/p/robotframework/issues/detail?id=967
  Check Test Case  ${TEST NAME}

*** Keywords ***
Verify List Variable Assigment
    [arguments]  ${test}  ${kw name}
    Should Be Equal  ${test.kws[0].name}  \@{listvar} = ExampleJavaLibrary.${kw name}
    Check Log Message  ${test.kws[0].msgs[0]}  \@{listvar} = [ v1 | v2 | v3 ]


