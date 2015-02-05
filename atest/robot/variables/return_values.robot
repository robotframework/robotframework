*** Settings ***
Documentation     Tests for return values from keywords. Tests include e.g.
...               setting different return values for variables and checking
...               messages that are automatically logged when variables are set.
...               See also return_values_java.robot.
Suite Setup       Run Tests    ${EMPTY}    variables/return_values.robot
Force Tags        regression    pybot    jybot
Resource          atest_resource.robot

*** Variables ***
${UNREPR STR}     <Unrepresentable object 'FailiningStr'. Error: *>
${UNREPR UNIC}    <Unrepresentable object 'FailiningUnicode'. Error: *>

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

Python Object To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = This is my name

None To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = None

Unrepresentable object to scalar variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = ${UNREPR STR}    pattern=yes

Multible Scalar Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${var1}, \${var2} = BuiltIn.Create List
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var1} = one
    Check Log Message    ${tc.kws[0].msgs[1]}    \${var2} = 2

Unrepresentable objects to scalar variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${o1} = ${UNREPR STR}    pattern=yes
    Check Log Message    ${tc.kws[0].msgs[1]}    \${o2} = ${UNREPR UNIC}    pattern=yes

Multiple Scalars With Too Few Values
    Check Test Case    ${TESTNAME}

Scalar Variables With More Values Than Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${a} = a
    Check Log Message    ${tc.kws[0].msgs[1]}    \${b} = b
    Check Log Message    ${tc.kws[0].msgs[2]}    \${c} = [*'c', 4]    pattern=yes

Multiple Scalars When No List Returned
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

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

Unrepresentable objects to list variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{unrepr} = [ ${UNREPR STR} | ${UNREPR UNIC} ]    pattern=yes
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{unrepr} = [ ${UNREPR STR} | ${UNREPR UNIC} ]    pattern=yes
    Should Match         ${tc.kws[2].kws[0].name}    \${obj} = ${UNREPR STR}
    Check Log Message    ${tc.kws[2].kws[0].kws[1].msgs[0]}    $\{var} = ${UNREPR STR}    pattern=yes
    Should Match         ${tc.kws[2].kws[1].name}    \${obj} = ${UNREPR UNIC}
    Check Log Message    ${tc.kws[2].kws[1].kws[1].msgs[0]}    $\{var} = ${UNREPR UNIC}    pattern=yes

List When No List Returned
    Check Test Case    ${TESTNAME}

Scalars And And List
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${first}, \@{rest} = BuiltIn.Evaluate
    Check Log Message    ${tc.kws[0].msgs[0]}    \${first} = 0
    Check Log Message    ${tc.kws[0].msgs[1]}    \@{rest} = [ 1 | 2 | 3 | 4 ]
    Should Be Equal    ${tc.kws[3].name}    \${a}, \${b}, \@{c} = BuiltIn.Create List
    Check Log Message    ${tc.kws[3].msgs[0]}    \${a} = 1
    Check Log Message    ${tc.kws[3].msgs[1]}    \${b} = 2
    Check Log Message    ${tc.kws[3].msgs[2]}    \@{c} = [ c | d | e | f ]

None To Multiple Scalar Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${x} = None
    Check Log Message    ${tc.kws[0].msgs[1]}    \${y} = None

None To List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    \@{list} = [ ]

None To Scalar Variables And List Variable
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

Long String To Scalar Variable
    [Documentation]    Long assing messages should be cut.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${v300} = 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 ...

Long Values To List Variable
    [Documentation]    Long assing messages should be cut.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    \@{long} = [ 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 | 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456...

No Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${nokeyword} = None

Failing Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${ret} = BuiltIn.Fail

Failing Keyword And Teardown
    Check Test Case    ${TESTNAME}

Assign Mark Without Space
    Check Test Case    ${TESTNAME}

No Assign Mark
    Check Test Case    ${TESTNAME}

Optional Assign Mark With Multiple Variables
    Check Test Case    ${TESTNAME}

Assign Mark Can Be Used Only With The Last Variable
    Check Test Case    ${TESTNAME}
