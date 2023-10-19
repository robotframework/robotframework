*** Settings ***
Documentation     Tests for return values from keywords. Tests include e.g.
...               setting different return values for variables and checking
...               messages that are automatically logged when variables are set.
Suite Setup       Run Tests    ${EMPTY}    variables/return_values.robot
Resource          atest_resource.robot

*** Variables ***
${UNREPR}         <Unrepresentable object FailingStr. Error: *>

*** Test Cases ***
Simple Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Set Variable    \${setvar}    this value is set
    Check Log Message    ${tc.kws[0].msgs[0]}    \${setvar} = this value is set

Empty Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${setvar} =

List To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${setvar} = ['a', 2]

Python Object To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = This is my name

Unrepresentable object to scalar variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = ${UNREPR}    pattern=yes

None To Scalar Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = None

Multible Scalar Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Create List    \${var1}, \${var2}    one, \${2}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var1} = one
    Check Log Message    ${tc.kws[0].msgs[1]}    \${var2} = 2

Unrepresentable objects to scalar variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${o1} = ${UNREPR}    pattern=yes
    Check Log Message    ${tc.kws[0].msgs[1]}    \${o2} = ${UNREPR}    pattern=yes

None To Multiple Scalar Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${x} = None
    Check Log Message    ${tc.kws[0].msgs[1]}    \${y} = None

Multiple Scalars With Too Few Values
    Check Test Case    ${TESTNAME}

Multiple Scalars With Too Many Values
    Check Test Case    ${TEST NAME}

Multiple Scalars When No List Returned
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Create List    \@{listvar}    h, e, ll, o
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{listvar} = [ h | e | ll | o ]

List Variable From Consumable Iterable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    ExampleLibrary.Return Consumable Iterable    \@{listvar}    Keijo, Mela
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{listvar} = [ Keijo | Mela ]

List Variable From List Subclass
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    ExampleLibrary.Return List Subclass    \@{listvar}    Keijo, Mela
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{listvar} = [ Keijo | Mela ]

List Variable From Dictionary
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{list} = [ name ]

Unrepresentable objects to list variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.body[0].msgs[0]}    \@{unrepr} = ? ${UNREPR} | ${UNREPR} ?    pattern=yes
    Check Log Message    ${tc.body[0].msgs[0]}    \@{unrepr} = ? ${UNREPR} | ${UNREPR} ?    pattern=yes
    Should Match         ${tc.body[2].body[0].assign['\${obj}']}   ${UNREPR}
    Check Log Message    ${tc.body[2].body[0].body[1].msgs[0]}     $\{var} = ${UNREPR}    pattern=yes
    Should Match         ${tc.body[2].body[1].assign['\${obj}']}   ${UNREPR}
    Check Log Message    ${tc.body[2].body[1].body[1].msgs[0]}     $\{var} = ${UNREPR}    pattern=yes

None To List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    \@{list} = [ ]

List When Non-List Returned
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Only One List Variable Allowed
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

List After Scalars
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Evaluate    \${first}, \@{rest}    range(5)
    Check Log Message    ${tc.kws[0].msgs[0]}    \${first} = 0
    Check Log Message    ${tc.kws[0].msgs[1]}    \@{rest} = [ 1 | 2 | 3 | 4 ]
    Check Keyword Data    ${tc.kws[3]}    BuiltIn.Create List    \${a}, \${b}, \@{c}    1, 2, c, d, e, f
    Check Log Message    ${tc.kws[3].msgs[0]}    \${a} = 1
    Check Log Message    ${tc.kws[3].msgs[1]}    \${b} = 2
    Check Log Message    ${tc.kws[3].msgs[2]}    \@{c} = [ c | d | e | f ]

List Before Scalars
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Set Variable    \@{list}, \${scalar}    \${1}, 2
    Check Log Message    ${tc.kws[0].msgs[0]}    \@{list} = [ 1 ]
    Check Log Message    ${tc.kws[0].msgs[1]}    \${scalar} = 2

List Between Scalars
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Set Variable    \${first}, \@{list}, \${last}    1, 2, 3, 4
    Check Log Message    ${tc.kws[0].msgs[0]}    \${first} = 1
    Check Log Message    ${tc.kws[0].msgs[1]}    \@{list} = [ 2 | 3 ]
    Check Log Message    ${tc.kws[0].msgs[2]}    \${last} = 4

None To Scalar Variables And List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${a} = None
    Check Log Message    ${tc.kws[0].msgs[1]}    \${b} = None
    Check Log Message    ${tc.kws[0].msgs[2]}    \${c} = None
    Check Log Message    ${tc.kws[0].msgs[3]}    \@{d} = [ ]

List and scalars with not enough values
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

Dictionary return value
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \&{ret} = { foo=bar | muu=mi }

None To Dict
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \&{ret} = { }

Dictionary is dot-accessible
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \&{dict} = { key=value }
    Check Log Message    ${tc.kws[2].msgs[0]}    \&{nested} = { key=value | nested={'key': 'nested value'} }

Scalar dictionary is not dot-accessible
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${normal} = {'key': 'value'}

Dictionary only allowed alone
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3
    Check Test Case    ${TEST NAME} 4
    Check Test Case    ${TEST NAME} 5

Dict when non-dict returned
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

Long String To Scalar Variable
    [Documentation]    Long assign messages should be cut.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${v300} = 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 ...

Long Values To List Variable
    [Documentation]    Long assign messages should be cut.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    \@{long} = [ 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 | 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456...

Big Items In Dictionary
    ${tc} =    Check Test Case    ${TEST NAME}
    ${v100} =    Evaluate    '1234567890' * 10
    Check Log Message    ${tc.kws[1].msgs[0]}    \&{big} = { _${v100}=${v100[:96]}...

No Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    ${EMPTY}    \${nokeyword}    status=FAIL

Failing Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Fail    \${ret}    Failing instead of returning    status=FAIL

Non-existing keyword
    ${tc1} =    Check Test Case    ${TEST NAME} 1
    ${tc2} =    Check Test Case    ${TEST NAME} 2
    Check Keyword Data    ${tc1.kws[0]}    I do not exist           \${x}    status=FAIL
    Check Keyword Data    ${tc2.kws[0]}    I do not exist either    \${x}    status=FAIL

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

Named based on another variable
    Check Test Case    ${TESTNAME}

Non-existing variable in name
    Check Test Case    ${TESTNAME}

Files are not lists
    Check Test Case    ${TESTNAME}

Invalid count error is catchable
    Check Test Case    ${TESTNAME}

Invalid type error is catchable
    Check Test Case    ${TESTNAME}

Invalid assign
    Check Test Case    ${TESTNAME}

Invalid assign with assign mark
    Check Test Case    ${TESTNAME}

Too many assign marks
    Check Test Case    ${TESTNAME}

Item assign to scalar dictionary
    ${tc}=  Check Test Case    ${TESTNAME}
    Check Log Message          ${tc.kws[1].msgs[0]}    \${dict_variable}[key_str1] = replaced_value
    Check Log Message          ${tc.kws[2].msgs[0]}    \${dict_variable}[\${0}] = 100
    Check Log Message          ${tc.kws[3].msgs[0]}    \${dict_variable}[0] = new_value

Nested item assign
    ${tc}=  Check Test Case    ${TESTNAME}
    Check Log Message          ${tc.kws[2].msgs[0]}    \${dict_variable}[list][0] = 101
    Check Log Message          ${tc.kws[3].msgs[0]}    \${dict_variable}[list][\${1}] = 102
    Check Log Message          ${tc.kws[4].msgs[0]}    \${dict_variable}[list][-1] = 103

Item assign to scalar list
    ${tc}=  Check Test Case    ${TESTNAME}
    Check Log Message          ${tc.kws[1].msgs[0]}    \${list_variable}[0] = 100
    Check Log Message          ${tc.kws[2].msgs[0]}    \${list_variable}[\${1}] = 101
    Check Log Message          ${tc.kws[3].msgs[0]}    \${list_variable}[-1] = 102

Slice assign to scalar list
    ${tc}=  Check Test Case    ${TESTNAME}
    Check Log Message          ${tc.kws[3].msgs[0]}    \${list_variable}[:2] = ['101', '102', '103']
    Check Log Message          ${tc.kws[4].msgs[0]}    \${list_variable}[-2:] = ['104']

Item assign using variable as index
    ${tc}=  Check Test Case    ${TESTNAME}
    Check Log Message          ${tc.kws[5].msgs[0]}    \${list_variable}[\${int_variable}] = 105
    Check Log Message          ${tc.kws[5].msgs[1]}    \${list_variable}[\${str_variable}] = 101
    Check Log Message          ${tc.kws[5].msgs[2]}    \${list_variable}[\${slice_variable}] = [102]
    Check Log Message          ${tc.kws[5].msgs[3]}    \${list_variable}[\${strslice_variable}] = [103, 104]

Item assign to object with setitem capability
    Check Test Case    ${TESTNAME}

Item assign to object without setitem capability fails
    Check Test Case    ${TESTNAME}

Item assign to immutable object fails
    Check Test Case    ${TESTNAME}

Item assign expects iterable fails
    Check Test Case    ${TESTNAME}

Index not found error when item assign to list
    Check Test Case    ${TESTNAME}

Item assign to undeclared scalar fails
    Check Test Case    ${TESTNAME}

Item assign to undeclared dict fails
    Check Test Case    ${TESTNAME}

Item assign to undeclared list fails
    Check Test Case    ${TESTNAME}

Empty item assign to list fails
    Check Test Case    ${TESTNAME}

Empty item assign to dictionary
    Check Test Case    ${TESTNAME}

Multiple item assigns to scalars only
    Check Test Case    ${TESTNAME}

Multiple item assigns to scalars and list
    Check Test Case    ${TESTNAME}

Multiple item assigns to scalars and list slice
    Check Test Case    ${TESTNAME}

Item assign without assign mark
    Check Test Case    ${TESTNAME}

Single item assign to list
    ${tc}=  Check Test Case    ${TESTNAME}
    Check Log Message          ${tc.kws[1].msgs[0]}    \@{list_variable}[1] = [ a | b | c ]

Single item assign to dict
    ${tc}=  Check Test Case    ${TESTNAME}
    Check Log Message          ${tc.kws[1].msgs[0]}    \&{dict_variable}[a] = { 0=1 | 2=3 }

Single item assign to list should fail if value is not list
    Check Test Case    ${TESTNAME}

Single item assign to dict should fail if value is not dict
    Check Test Case    ${TESTNAME}
