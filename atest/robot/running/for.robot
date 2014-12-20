*** Settings ***
Documentation   For loop
Suite Setup     Run Tests  ${EMPTY}  running/for.robot
Force Tags      regression  pybot  jybot
Resource        atest_resource.robot

*** Variables ***
${SYNTAX_ERROR}  Syntax error: Invalid syntax in FOR loop. Expected format:\n | : FOR | \${var} | IN | item1 | item2 |

*** Test Cases ***
Simple For
    ${test} =  Check Test Case  Simple For
    Check Log Message  ${test.kws[0].msgs[0]}  Not yet in For
    Should Be For Keyword  ${test.kws[1]}  2
    Should Be For Item  ${test.kws[1].kws[0]}  \${var} = one
    Check Log Message  ${test.kws[1].kws[0].kws[0].msgs[0]}  var: one
    Should Be For Item  ${test.kws[1].kws[1]}  \${var} = two
    Check Log Message  ${test.kws[1].kws[1].kws[0].msgs[0]}  var: two
    Check Log Message  ${test.kws[2].msgs[0]}  Not in For anymore
    ${test2} =  Check Test Case  Simple For 2
    Should Be For Keyword  ${test2.kws[0]}  6
    Test "Simple For 2" Helper  ${test2.kws[0].kws[0]}  1
    Test "Simple For 2" Helper  ${test2.kws[0].kws[1]}  2
    Test "Simple For 2" Helper  ${test2.kws[0].kws[2]}  3
    Test "Simple For 2" Helper  ${test2.kws[0].kws[3]}  4
    Test "Simple For 2" Helper  ${test2.kws[0].kws[4]}  5
    Test "Simple For 2" Helper  ${test2.kws[0].kws[5]}  6

Empty For
    ${test} =  Check Test Case  Empty for
    Should Be For Keyword  ${test.kws[0]}  0

For Without Value
    ${test} =  Check Test Case  For Without value
    Should Be For Keyword  ${test.kws[0]}  0

For Loop Over Empty List Var
    Check Test Case  ${TESTNAME}

For Failing
    ${test} =  Check Test Case  For Failing
    Should Be For Keyword  ${test.kws[0]}  1
    Equals  ${test.kws[0].kws[0].status}  FAIL
    Check Log Message  ${test.kws[0].kws[0].kws[0].msgs[0]}  Hello before failing kw
    Ints Equal  ${test.kws[0].kws[0].keyword_count}  2
    ${test2} =  Check Test Case  For Failing 2
    Should Be For Keyword  ${test2.kws[0]}  4
    Check Log Message  ${test2.kws[0].kws[2].kws[0].msgs[0]}  Before Check
    Check Log Message  ${test2.kws[0].kws[2].kws[2].msgs[0]}  After Check
    Check Log Message  ${test2.kws[0].kws[3].kws[0].msgs[0]}  Before Check
    Ints Equal  ${test2.kws[0].kws[3].keyword_count}  2

For With User Keywords
    ${test} =  Check Test Case  For with User Keywords
    Should Be For Keyword  ${test.kws[0]}  2
    Check KW "My UK"  ${test.kws[0].kws[0].kws[0]}
    Check KW "My UK 2"  ${test.kws[0].kws[0].kws[1]}  foo
    Check KW "My UK"  ${test.kws[0].kws[1].kws[0]}
    Check KW "My UK 2"  ${test.kws[0].kws[1].kws[1]}  bar

For With Failures In User Keywords
    ${test} =  Check Test Case  For With Failures In User Keywords
    Should Be For Keyword  ${test.kws[0]}  2

Many Fors In One Test
    ${test} =  Check Test Case  Many Fors in One Test
    Should Be For Keyword  ${test.kws[0]}  2
    Check Log Message  ${test.kws[0].kws[0].kws[0].msgs[0]}  In first for with var "foo"
    Check Log Message  ${test.kws[0].kws[1].kws[0].msgs[0]}  In first for with var "bar"
    Should Be For Keyword  ${test.kws[1]}  1
    Check KW "My UK 2"  ${test.kws[1].kws[0].kws[0]}  Hello, world!
    Check Log Message  ${test.kws[2].msgs[0]}  Outside for loop
    Should Be For Keyword  ${test.kws[3]}  2
    Check Log Message  ${test.kws[3].kws[0].kws[0].msgs[0]}  Third for loop
    Check Log Message  ${test.kws[3].kws[0].kws[2].msgs[0]}  Value: a
    Check Log Message  ${test.kws[3].kws[1].kws[0].msgs[0]}  Third for loop
    Check Log Message  ${test.kws[3].kws[1].kws[2].msgs[0]}  Value: b
    Check Log Message  ${test.kws[4].msgs[0]}  End of the test

For With Values In Multiple Rows
    ${test} =  Check Test Case  For With Values In Multiple Rows
    Should Be For Keyword  ${test.kws[0]}  10
    Check Log Message  ${test.kws[0].kws[0].kws[0].msgs[0]}  1
    @{indexes} =  Evaluate  range(10)
    :FOR  ${i}  IN  @{indexes}
    \  ${exp} =  Evaluate  str(${i} + 1)
    \  Check Log Message  ${test.kws[0].kws[${i}].kws[0].msgs[0]}  ${exp}
    Message  Sanity check:
    Check Log Message  ${test.kws[0].kws[0].kws[0].msgs[0]}  1
    Check Log Message  ${test.kws[0].kws[4].kws[0].msgs[0]}  5
    Check Log Message  ${test.kws[0].kws[9].kws[0].msgs[0]}  10

For With Keyword Args On Multiple Rows
    ${test} =  Check Test Case  For With Keyword Args On Multiple Rows
    Should Be For Keyword  ${test.kws[0]}  2
    Check Log Message  ${test.kws[0].kws[0].kws[1].msgs[0]}  1 2 3 4 5 6 7 one
    Check Log Message  ${test.kws[0].kws[1].kws[1].msgs[0]}  1 2 3 4 5 6 7 two

For In User Keywords
    ${test} =  Check Test Case  For In User Keywords
    Check KW "For In UK"  ${test.kws[0]}
    Check KW "For In UK with Args"  ${test.kws[1]}  4  one

Nested For In User Keywords
    ${test} =  Check Test Case  Nested For In User Keywords
    Check KW "Nested For In UK"  ${test.kws[0]}  foo

For In Test And User Keywords
    ${test} =  Check Test Case  For in Test And user Keywords
    Should Be For Keyword  ${test.kws[1]}  1
    Check KW "For In UK"  ${test.kws[1].kws[0].kws[0]}
    Check KW "For In UK with Args"  ${test.kws[1].kws[0].kws[1]}  2  one
    Check KW "Nested For In UK"  ${test.kws[1].kws[0].kws[2]}  one

For Variable Scope
    Check Test Case  For Variable Scope

For With Set
    ${test} =  Check Test Case  For With Set
    Should Be For Keyword  ${test.kws[0]}  2
    Check Log Message  ${test.kws[0].kws[0].kws[0].msgs[0]}  \${v1} = value 1
    Check Log Message  ${test.kws[0].kws[0].kws[1].msgs[0]}  \${v2} = value 2
    Check Log Message  ${test.kws[0].kws[0].kws[1].msgs[1]}  \${v3} = value 3
    Check Log Message  ${test.kws[0].kws[0].kws[2].msgs[0]}  \@{list} = [ 1 | 2 | 3 | y ]
    Check Log Message  ${test.kws[0].kws[1].kws[0].msgs[0]}  \${v1} = value 1
    Check Log Message  ${test.kws[0].kws[1].kws[1].msgs[0]}  \${v2} = value 2
    Check Log Message  ${test.kws[0].kws[1].kws[1].msgs[1]}  \${v3} = value 3
    Check Log Message  ${test.kws[0].kws[1].kws[2].msgs[0]}  \@{list} = [ 1 | 2 | 3 | z ]

For Without In
    Check Test Case  For Without In 1
    Check Test Case  For Without In 2
    Check Test Case  For Without In 3

For Without Parameters
    Check Test Case  For Without Parameters

For Without Variable
    Check Test Case  For without variable

Variable Format
    Check Test Case  Variable Format 1
    Check Test Case  Variable Format 2
    Check Test Case  Variable Format 3
    Check Test Case  Variable Format 4

For With Non Existing Keyword
    Check Test Case  For With Non Existing Keyword

For With Non Existing Variable
    Check Test Case  For With Non Existing Variable

For With Invalid Set
    Check Test Case  For With Invalid Set

For With Multiple Variables
    ${test} =  Check Test Case  For with multiple variables
    Should Be For Keyword  ${test.kws[0]}  4
    Should Be For Item  ${test.kws[0].kws[0]}  \${x} = 1, \${y} = a
    Check Log Message  ${test.kws[0].kws[0].kws[0].msgs[0]}  1a
    Should Be For Item  ${test.kws[0].kws[1]}  \${x} = 2, \${y} = b
    Check Log Message  ${test.kws[0].kws[1].kws[0].msgs[0]}  2b
    Should Be For Item  ${test.kws[0].kws[2]}  \${x} = 3, \${y} = c
    Check Log Message  ${test.kws[0].kws[2].kws[0].msgs[0]}  3c
    Should Be For Item  ${test.kws[0].kws[3]}  \${x} = 4, \${y} = d
    Check Log Message  ${test.kws[0].kws[3].kws[0].msgs[0]}  4d
    Should Be For Keyword  ${test.kws[2]}  2
    Should Be For Item  ${test.kws[2].kws[0]}  \${a} = 1, \${b} = 2, \${c} = 3, \${d} = 4, \${e} = 5
    Should Be For Item  ${test.kws[2].kws[1]}  \${a} = 1, \${b} = 2, \${c} = 3, \${d} = 4, \${e} = 5

For With Wrong Number Of Parameters For Multiple Variables
    ${test} =  Check Test Case  For With Wrong number of parameters for multiple variables
    Should Be For Keyword  ${test.kws[1]}  0

Cut Long Variable Value In For Item Name
    ${test} =  Check Test Case  Cut Long Variable Value In For Item Name
    ${exp10} =  Set  0123456789
    ${exp100} =  Evaluate  "${exp10}" * 10
    ${exp200} =  Evaluate  "${exp10}" * 20
    ${exp200+} =  Set  ${exp200}...
    Should Be For Keyword  ${test.kws[6]}  6
    Should Be For Item  ${test.kws[6].kws[0]}  \${var} = ${exp10}
    Should Be For Item  ${test.kws[6].kws[1]}  \${var} = ${exp100}
    Should Be For Item  ${test.kws[6].kws[2]}  \${var} = ${exp200}
    Should Be For Item  ${test.kws[6].kws[3]}  \${var} = ${exp200+}
    Should Be For Item  ${test.kws[6].kws[4]}  \${var} = ${exp200+}
    Should Be For Item  ${test.kws[6].kws[5]}  \${var} = ${exp200+}
    Should Be For Keyword  ${test.kws[7]}  2
    Should Be For Item  ${test.kws[7].kws[0]}  \${var1} = ${exp10}, \${var2} = ${exp100}, \${var3} = ${exp200}
    Should Be For Item  ${test.kws[7].kws[1]}  \${var1} = ${exp200+}, \${var2} = ${exp200+}, \${var3} = ${exp200+}

For with illegal xml characters
    ${test} =  Check Test Case      ${TEST NAME}
    Should be equal  ${test.kws[0].kws[0].name}    \${var} = illegal:
    Should be equal  ${test.kws[0].kws[1].name}    \${var} = more:

For In Range
    ${test} =  Check Test Case  For In Range
    Should Be For In Range Keyword  ${test.kws[1]}  100
    Should Be For Item  ${test.kws[1].kws[0]}  \${i} = 0
    Check Log Message  ${test.kws[1].kws[0].kws[1].msgs[0]}  i: 0
    Should Be For Item  ${test.kws[1].kws[1]}  \${i} = 1
    Check Log Message  ${test.kws[1].kws[1].kws[1].msgs[0]}  i: 1
    Should Be For Item  ${test.kws[1].kws[42]}  \${i} = 42
    Check Log Message  ${test.kws[1].kws[42].kws[1].msgs[0]}  i: 42
    Should Be For Item  ${test.kws[1].kws[-1]}  \${i} = 99
    Check Log Message  ${test.kws[1].kws[-1].kws[1].msgs[0]}  i: 99

For In Range With Start And Stop
    Check Test Case  For In Range With Start And Stop

For In Range With Start, Stop And Step
    ${test} =  Check Test Case  For In Range With Start, Stop and Step
    Should Be For In Range Keyword  ${test.kws[1]}  3
    Should Be For Item  ${test.kws[1].kws[0]}  \${myvar} = 10
    Should Be For Item  ${test.kws[1].kws[1]}  \${myvar} = 7
    Should Be For Item  ${test.kws[1].kws[2]}  \${myvar} = 4

For In Range With Variables In Arguments
    Check Test Case  For In Range With Variables In Arguments

For In Range With Expressions in Arguments
    Check Test Case  For In Range With Expressions in Arguments

For In Range With Multiple Variables
    ${test} =  Check Test Case  For In Range With Multiple Variables
    Should Be For In Range Keyword  ${test.kws[1]}  4
    Should Be For Item  ${test.kws[1].kws[0]}  \${i} = -1, \${j} = 0, \${k} = 1
    Should Be For Item  ${test.kws[1].kws[1]}  \${i} = 2, \${j} = 3, \${k} = 4
    Should Be For Item  ${test.kws[1].kws[2]}  \${i} = 5, \${j} = 6, \${k} = 7
    Should Be For Item  ${test.kws[1].kws[3]}  \${i} = 8, \${j} = 9, \${k} = 10

For In Range With Too Many Arguments
    ${test} =  Check Test Case  For In Range With Too Many Arguments
    Should Be For In Range Keyword  ${test.kws[0]}  0

For In Range With No Arguments
    Check Test Case  For In Range With No Arguments

For In Range With Non Number Arguments
    Check Test Case  For In Range With Non Number Arguments

For In Range With Wrong Number Of Variables
    Check Test Case  For In Range With Wrong Number Of Variables

For In Range With Non-Existing Variables In Arguments
    Check Test Case  For In Range With Non-Existing Variables In Arguments

For In Range With None As Range
    Check Test Case  ${TESTNAME}

For loops are case and space insensitive
    Check Test Case  ${TESTNAME}

For word can have many colons
    Check Test Case  ${TESTNAME}

For In Range With Float Start, Stop And Step
    ${test} =  Check Test Case  For In Range With Float Start, Stop and Step
    Should Be For In Range Keyword  ${test.kws[1]}  3
    Should Be For Item  ${test.kws[1].kws[0]}  \${myvar} = 10.99
    Should Be For Item  ${test.kws[1].kws[1]}  \${myvar} = 7.95
    Should Be For Item  ${test.kws[1].kws[2]}  \${myvar} = 4.91

*** Keywords ***
Should Be For Keyword
    [Arguments]  ${kw}  ${subcount}
    Equals  ${kw.type}  for  Not FOR keyword
    Contains  ${kw.name}  IN  Not FOR keyword
    Ints Equal  ${kw.keyword_count}  ${subcount}  Wrong number of sub keywords

Should Be For In Range Keyword
    [Arguments]  ${kw}  ${subcount}
    Should Be For Keyword  ${kw}  ${subcount}
    Contains  ${kw.name}  IN RANGE  Not FOR IN RANGE keyword

Should Be For Item
    [Arguments]  ${kw}  ${name}
    Equals  ${kw.type}  foritem  Not FOR item
    Equals  ${kw.name}  ${name}

Test "Simple For 2" Helper
    [Arguments]  ${kw}  ${num}
    Check Log Message  ${kw.kws[0].msgs[0]}  ${num}
    Check Log Message  ${kw.kws[1].msgs[0]}  Hello from for loop
    Equals  ${kw.kws[2].name}  BuiltIn.No Operation

Test "For With Repeat" Helper
    [Arguments]  ${kw}  ${num}
    Equals  ${kw.kws[0].name}  0x BuiltIn.Fail
    Check Log Message  ${kw.kws[1].msgs[1]}  Executed once
    Equals  ${kw.kws[2].name}  2x My UK
    Equals  ${kw.kws[2].kws[0].name}  BuiltIn.No Operation
    Check Log Message  ${kw.kws[2].kws[1].msgs[0]}  We are in My UK
    Equals  ${kw.kws[2].kws[2].name}  BuiltIn.No Operation
    Check Log Message  ${kw.kws[2].kws[3].msgs[0]}  We are in My UK
    Equals  ${kw.kws[3].name}  ${num}x BuiltIn.Log
    Check Log Message  ${kw.kws[3].msgs[1]}  Executed ${num} times
    Check Log Message  ${kw.kws[4].msgs[1]}  Executed 5 times
    Check Log Message  ${kw.kws[4].msgs[1]}  Executed 5 times
    Check Log Message  ${kw.kws[4].msgs[2]}  Executed 5 times
    Check Log Message  ${kw.kws[4].msgs[3]}  Executed 5 times
    Check Log Message  ${kw.kws[4].msgs[4]}  Executed 5 times

Check KW "My UK"
    [Arguments]  ${kw}
    Equals  ${kw.name}  My UK
    Equals  ${kw.kws[0].name}  BuiltIn.No Operation
    Check Log Message  ${kw.kws[1].msgs[0]}  We are in My UK

Check KW "My UK 2"
    [Arguments]  ${kw}  ${arg}
    Equals  ${kw.name}  My UK 2
    Check KW "My UK"  ${kw.kws[0]}
    Check Log Message  ${kw.kws[1].msgs[0]}  My UK 2 got argument "${arg}"
    Check KW "My UK"  ${kw.kws[2]}

Check KW "For In UK"
    [Arguments]  ${kw}
    Equals  ${kw.name}  For In UK
    Check Log Message  ${kw.kws[0].msgs[0]}  Not for yet
    Should Be For Keyword  ${kw.kws[1]}  2
    Check Log Message  ${kw.kws[1].kws[0].kws[0].msgs[0]}  This is for with 1
    Check KW "My UK"  ${kw.kws[1].kws[0].kws[1]}
    Check Log Message  ${kw.kws[1].kws[1].kws[0].msgs[0]}  This is for with 2
    Check KW "My UK"  ${kw.kws[1].kws[1].kws[1]}
    Check Log Message  ${kw.kws[2].msgs[0]}  Not for anymore

Check KW "For In UK With Args"
    [Arguments]  ${kw}  ${arg_count}  ${first_arg}
    Equals  ${kw.name}  For In UK With Args
    Should Be For Keyword  ${kw.kws[0]}  ${arg_count}
    Check KW "My UK 2"  ${kw.kws[0].kws[0].kws[0]}  ${first_arg}
    Should Be For Keyword  ${kw.kws[1]}  1
    Check Log Message  ${kw.kws[1].kws[0].kws[0].msgs[0]}  This for loop is executed only once

Check KW "Nested For In UK"
    [Arguments]  ${kw}  ${first_arg}
    Should Be For Keyword  ${kw.kws[0]}  1
    Check KW "For In UK"  ${kw.kws[0].kws[0].kws[0]}
    ${nested2} =  Set  ${kw.kws[0].kws[0].kws[1]}
    Equals  ${nested2.name}  Nested For In UK 2
    Should Be For Keyword  ${nested2.kws[0]}  2
    Check KW "For In UK"  ${nested2.kws[0].kws[0].kws[0]}
    Check Log Message  ${nested2.kws[0].kws[0].kws[1].msgs[0]}  Got arg: ${first_arg}
    Check Log Message  ${nested2.kws[1].msgs[0]}  This ought to be enough    FAIL

