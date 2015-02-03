*** Settings ***
Documentation     Tests for return values from keywords. Tests include e.g.
...               setting different return values for variables and checking
...               messages that are automatically logged when variables are set.
...               See also return_values_java.robot.
Suite Setup       Run Tests    ${EMPTY}    variables/return_values.robot
Force Tags        regression    pybot    jybot
Resource          atest_resource.robot

*** Test Cases ***
Simple Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${setvar} = BuiltIn.Set Variable
    Check Log Message    ${tc.kws[0].msgs[0]}    \${setvar} = this value is set

Empty Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${setvar} =

List To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${setvar} = [*'a', 2]    pattern=yep

Multible Scalar Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${var1}, \${var2} = BuiltIn.Create List
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var1} = one
    Check Log Message    ${tc.kws[0].msgs[1]}    \${var2} = two

= Mark Without Space
    Check Test Case    ${TEST NAME}

No = Mark
    Check Test Case    ${TEST NAME}

Optional = Mark With Multiple Variables
    Check Test Case    ${TEST NAME}

= Can Be Used Only With The Last Variable
    Check Test Case    ${TEST NAME}

Python Object To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = This is my name

None To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = None

List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \@{listvar} = BuiltIn.Create List
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{listvar} = [ h | e | ll | o ]

List Variable From Custom Iterable
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \@{listvar} = ExampleLibrary.Return Custom Iterable
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{listvar} = [ Keijo | Mela ]

List Variable From List Subclass
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \@{listvar} = ExampleLibrary.Return List Subclass
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{listvar} = [ Keijo | Mela ]

List Variable From Dictionary
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{list} = [ name ]

Long String To Scalar Variable
    [Documentation]    Long assing messages should be cut.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var_300} = 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890...

Long Values To List Variable
    [Documentation]    Long assing messages should be cut.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    \@{listvar} = [ 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890 | 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 12345...

Scalar Variables With More Values Than Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${a} = a
    Check Log Message    ${tc.kws[0].msgs[1]}    \${b} = b
    Check Log Message    ${tc.kws[0].msgs[2]}    \${c} = [*'c', 4]    pattern=yes

Multiple Scalars With Too Few Values
    Check Test Case    ${TEST NAME}

Multiple Scalars When No List Returned
    Check Test Case    ${TEST NAME}

List When No List Returned
    Check Test Case    ${TEST NAME}

List To Scalar And List Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${a}, \${b}, \@{c} = BuiltIn.Create List
    Check Log Message    ${tc.kws[0].msgs[0]}    \${a} = 1
    Check Log Message    ${tc.kws[0].msgs[1]}    \${b} = 2
    Check Log Message    ${tc.kws[0].msgs[2]}    \@{c} = [ c | d | e | f ]

One None To Multiple Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${x} = None
    Check Log Message    ${tc.kws[0].msgs[1]}    \${y} = None

One None To List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    \@{list} = [ ]

One None To Scalar Variables And List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${a} = None
    Check Log Message    ${tc.kws[0].msgs[1]}    \${b} = None
    Check Log Message    ${tc.kws[0].msgs[2]}    \${c} = None
    Check Log Message    ${tc.kws[0].msgs[3]}    \@{d} = [ ]

List Variable Can Be Only Last
    ${tc} =    Check Test Case    ${TEST NAME} 1
    Should Be Equal    ${tc.kws[0].name}    \@{list}, \@{list2} = BuiltIn.Set Variable
    ${tc} =    Check Test Case    ${TEST NAME} 2
    Should Be Equal    ${tc.kws[0].name}    \@{list}, \${scalar} = BuiltIn.Set Variable

No Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${nokeyword} = None

Failing keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${ret} = BuiltIn.Fail

Failing keyword and teardown
    Check Test Case    ${TEST NAME}

Return Unrepresentable Objects
    [Documentation]    See http://code.google.com/p/robotframework/issues/detail?id=967
    Check Test Case    ${TEST NAME}
