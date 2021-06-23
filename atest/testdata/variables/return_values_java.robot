*** Settings ***
Library           ExampleJavaLibrary

*** Test Cases ***
Set Multiple Scalar Variables Using Array
    ${var1}    ${var2} =    Get String Array    first value    second value
    Should Be Equal    ${var1}    first value
    Should Be Equal    ${var2}    second value
    ${i1}    ${i2}    ${i42} =    Get Array Of Three Ints
    Should Be Equal    ${i1}    ${1}
    Should Be Equal    ${i2}    ${2}
    Should Be Equal    ${i42}    ${42}

Set Object To Scalar Variable
    ${var} =    ExampleJavaLibrary.GetJavaObject    This is my name in Java
    Should Be Equal    ${var.name}    This is my name in Java

Set List Variable Using Array
    @{listvar} =    Get String Array    v1    v2    v3
    Should Be Equal    ${listvar}[0]    v1
    Should Be True    ${listvar} == ['v1', 'v2', 'v3']
    @{listvar} =    Get Array of Three Ints
    Should Be Equal    ${listvar}[0]    ${1}
    Should Be True    ${listvar} == [1 ,2, 42]

Set List Variable Using Vector
    @{listvar} =    Get String Vector    v1    v2    v3
    Should Be Equal    ${listvar}[0]    v1
    Should Be True    ${listvar} == ['v1', 'v2', 'v3']

Set List Variable Using Array List
    @{listvar} =    Get String Array List    v1    v2    v3
    Should Be Equal    ${listvar}[0]    v1
    Should Be True    ${listvar} == ['v1', 'v2', 'v3']

Set List Variable Using String List
    @{listvar} =    Get String List    v1    v2    v3
    Should Be Equal    ${listvar}[0]    v1
    Should Be True    ${listvar} == ['v1', 'v2', 'v3']

Set List Variable Using String Iterator
    @{listvar} =    Get String Iterator    v1    v2    v3
    Should Be Equal    ${listvar}[0]    v1
    Should Be True    ${listvar} == ['v1', 'v2', 'v3']

List Variable From Mapping
    @{list} =    Get Hashtable
    Should Be True    ${list} == []

Set Scalar Variables With More Values Than Variables Using Array
    [Documentation]    FAIL Cannot set variables: Expected 3 return values, got 6.
    ${a}    ${b}    ${c} =    Get String Array    a    b    c    d    e    f

Set Multiple Scalars With Too Few Values Using Array
    [Documentation]    FAIL Cannot set variables: Expected 4 return values, got 3.
    ${i1}    ${i2}    ${i3}    ${i4} =    Get Array Of Three Ints

Set List To Scalar And List Variables Using Array
    ${a}    ${b}    @{c} =    Get Array Of Three Ints
    Should Be Equal    ${a}    ${1}
    Should Be Equal    ${b}    ${2}
    Should Be Equal    @{c}    ${42}

Return Unrepresentable Object
    ${ret}=    Return Unrepresentable Object
