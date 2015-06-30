*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for.robot
Force Tags        regression    pybot    jybot
Resource          atest_resource.robot

*** Test Cases ***
Simple For
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Not yet in For
    Should Be For Keyword    ${tc.kws[1]}    2
    Should Be For Item    ${tc.kws[1].kws[0]}    \${var} = one
    Check Log Message    ${tc.kws[1].kws[0].kws[0].msgs[0]}    var: one
    Should Be For Item    ${tc.kws[1].kws[1]}    \${var} = two
    Check Log Message    ${tc.kws[1].kws[1].kws[0].msgs[0]}    var: two
    Check Log Message    ${tc.kws[2].msgs[0]}    Not in For anymore
    ${tc2} =    Check Test Case    ${TEST NAME} 2
    Should Be For Keyword    ${tc2.kws[0]}    6
    Test "Simple For 2" Helper    ${tc2.kws[0].kws[0]}    1
    Test "Simple For 2" Helper    ${tc2.kws[0].kws[1]}    2
    Test "Simple For 2" Helper    ${tc2.kws[0].kws[2]}    3
    Test "Simple For 2" Helper    ${tc2.kws[0].kws[3]}    4
    Test "Simple For 2" Helper    ${tc2.kws[0].kws[4]}    5
    Test "Simple For 2" Helper    ${tc2.kws[0].kws[5]}    6

Empty For Body Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    0

For Without Value Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    0

For Loop Over Empty List Variable Is Ok
    Check Test Case    ${TEST NAME}

For Loop Over Generator
    Check Test Case    ${TEST NAME}

For Failing
    ${tc} =    Check Test Case    ${TEST NAME} 1
    Should Be For Keyword    ${tc.kws[0]}    1
    Should Be Equal    ${tc.kws[0].kws[0].status}    FAIL
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    Hello before failing kw
    Should Be Equal As Integers    ${tc.kws[0].kws[0].keyword_count}    2
    ${tc2} =    Check Test Case    ${TEST NAME} 2
    Should Be For Keyword    ${tc2.kws[0]}    4
    Check Log Message    ${tc2.kws[0].kws[2].kws[0].msgs[0]}    Before Check
    Check Log Message    ${tc2.kws[0].kws[2].kws[2].msgs[0]}    After Check
    Check Log Message    ${tc2.kws[0].kws[3].kws[0].msgs[0]}    Before Check
    Should Be Equal As Integers    ${tc2.kws[0].kws[3].keyword_count}    2

For With Values On Multiple Rows
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    10
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    1
    : FOR    ${i}    IN RANGE    10
    \    ${exp} =    Evaluate    str(${i} + 1)
    \    Check Log Message    ${tc.kws[0].kws[${i}].kws[0].msgs[0]}    ${exp}
    # Sanity check
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    1
    Check Log Message    ${tc.kws[0].kws[4].kws[0].msgs[0]}    5
    Check Log Message    ${tc.kws[0].kws[9].kws[0].msgs[0]}    10

For With Keyword Args On Multiple Rows
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    2
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    1 2 3 4 5 6 7 one
    Check Log Message    ${tc.kws[0].kws[1].kws[1].msgs[0]}    1 2 3 4 5 6 7 two

Many Fors In One Test
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    2
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    In first for with var "foo"
    Check Log Message    ${tc.kws[0].kws[1].kws[0].msgs[0]}    In first for with var "bar"
    Should Be For Keyword    ${tc.kws[1]}    1
    Check KW "My UK 2"    ${tc.kws[1].kws[0].kws[0]}    Hello, world!
    Check Log Message    ${tc.kws[2].msgs[0]}    Outside for loop
    Should Be For Keyword    ${tc.kws[3]}    2
    Check Log Message    ${tc.kws[3].kws[0].kws[0].msgs[0]}    Third for loop
    Check Log Message    ${tc.kws[3].kws[0].kws[2].msgs[0]}    Value: a
    Check Log Message    ${tc.kws[3].kws[1].kws[0].msgs[0]}    Third for loop
    Check Log Message    ${tc.kws[3].kws[1].kws[2].msgs[0]}    Value: b
    Check Log Message    ${tc.kws[4].msgs[0]}    End of the test

For With User Keywords
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    2
    Check KW "My UK"    ${tc.kws[0].kws[0].kws[0]}
    Check KW "My UK 2"    ${tc.kws[0].kws[0].kws[1]}    foo
    Check KW "My UK"    ${tc.kws[0].kws[1].kws[0]}
    Check KW "My UK 2"    ${tc.kws[0].kws[1].kws[1]}    bar

For With Failures In User Keywords
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    2

For In User Keywords
    ${tc} =    Check Test Case    ${TEST NAME}
    Check KW "For In UK"    ${tc.kws[0]}
    Check KW "For In UK with Args"    ${tc.kws[1]}    4    one

Nested For In User Keywords
    ${tc} =    Check Test Case    ${TEST NAME}
    Check KW "Nested For In UK"    ${tc.kws[0]}    foo

For In Test And User Keywords
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[1]}    1
    Check KW "For In UK"    ${tc.kws[1].kws[0].kws[0]}
    Check KW "For In UK with Args"    ${tc.kws[1].kws[0].kws[1]}    2    one
    Check KW "Nested For In UK"    ${tc.kws[1].kws[0].kws[2]}    one

For Variable Scope
    Check Test Case    ${TEST NAME}

For With Assign
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    2
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    \${v1} = value 1
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    \${v2} = value 2
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[1]}    \${v3} = value 3
    Check Log Message    ${tc.kws[0].kws[0].kws[2].msgs[0]}    \@{list} = [ 1 | 2 | 3 | y ]
    Check Log Message    ${tc.kws[0].kws[1].kws[0].msgs[0]}    \${v1} = value 1
    Check Log Message    ${tc.kws[0].kws[1].kws[1].msgs[0]}    \${v2} = value 2
    Check Log Message    ${tc.kws[0].kws[1].kws[1].msgs[1]}    \${v3} = value 3
    Check Log Message    ${tc.kws[0].kws[1].kws[2].msgs[0]}    \@{list} = [ 1 | 2 | 3 | z ]

For With Invalid Assign
    Check Test Case    ${TEST NAME}

For Without In
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

For Without Parameters
    Check Test Case    ${TEST NAME}

For Without Variable
    Check Test Case    ${TEST NAME}

Variable Format
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3
    Check Test Case    ${TEST NAME} 4

For With Non Existing Keyword
    Check Test Case    ${TEST NAME}

For With Non Existing Variable
    Check Test Case    ${TEST NAME}

For With Multiple Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For Keyword    ${tc.kws[0]}    4
    Should Be For Item    ${tc.kws[0].kws[0]}    \${x} = 1, \${y} = a
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    1a
    Should Be For Item    ${tc.kws[0].kws[1]}    \${x} = 2, \${y} = b
    Check Log Message    ${tc.kws[0].kws[1].kws[0].msgs[0]}    2b
    Should Be For Item    ${tc.kws[0].kws[2]}    \${x} = 3, \${y} = c
    Check Log Message    ${tc.kws[0].kws[2].kws[0].msgs[0]}    3c
    Should Be For Item    ${tc.kws[0].kws[3]}    \${x} = 4, \${y} = d
    Check Log Message    ${tc.kws[0].kws[3].kws[0].msgs[0]}    4d
    Should Be For Keyword    ${tc.kws[2]}    2
    Should Be For Item    ${tc.kws[2].kws[0]}    \${a} = 1, \${b} = 2, \${c} = 3, \${d} = 4, \${e} = 5
    Should Be For Item    ${tc.kws[2].kws[1]}    \${a} = 1, \${b} = 2, \${c} = 3, \${d} = 4, \${e} = 5

For With Non-Matching Number Of Parameters And Variables
    ${tc} =    Check Test Case    ${TEST NAME} 1
    Should Be For Keyword    ${tc.kws[1]}    0
    ${tc} =    Check Test Case    ${TEST NAME} 2
    Should Be For Keyword    ${tc.kws[1]}    0

Cut Long Variable Value In For Item Name
    ${tc} =    Check Test Case    ${TEST NAME}
    ${exp10} =    Set Variable    0123456789
    ${exp100} =    Evaluate    "${exp10}" * 10
    ${exp200} =    Evaluate    "${exp10}" * 20
    ${exp200+} =    Set Variable    ${exp200}...
    Should Be For Keyword    ${tc.kws[6]}    6
    Should Be For Item    ${tc.kws[6].kws[0]}    \${var} = ${exp10}
    Should Be For Item    ${tc.kws[6].kws[1]}    \${var} = ${exp100}
    Should Be For Item    ${tc.kws[6].kws[2]}    \${var} = ${exp200}
    Should Be For Item    ${tc.kws[6].kws[3]}    \${var} = ${exp200+}
    Should Be For Item    ${tc.kws[6].kws[4]}    \${var} = ${exp200+}
    Should Be For Item    ${tc.kws[6].kws[5]}    \${var} = ${exp200+}
    Should Be For Keyword    ${tc.kws[7]}    2
    Should Be For Item    ${tc.kws[7].kws[0]}    \${var1} = ${exp10}, \${var2} = ${exp100}, \${var3} = ${exp200}
    Should Be For Item    ${tc.kws[7].kws[1]}    \${var1} = ${exp200+}, \${var2} = ${exp200+}, \${var3} = ${exp200+}

For with illegal xml characters
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be equal    ${tc.kws[0].kws[0].name}    \${var} = illegal:
    Should be equal    ${tc.kws[0].kws[1].name}    \${var} = more:

For In Range
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For In Range Keyword    ${tc.kws[0]}    100
    Should Be For Item    ${tc.kws[0].kws[0]}    \${i} = 0
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    i: 0
    Should Be For Item    ${tc.kws[0].kws[1]}    \${i} = 1
    Check Log Message    ${tc.kws[0].kws[1].kws[1].msgs[0]}    i: 1
    Should Be For Item    ${tc.kws[0].kws[42]}    \${i} = 42
    Check Log Message    ${tc.kws[0].kws[42].kws[1].msgs[0]}    i: 42
    Should Be For Item    ${tc.kws[0].kws[-1]}    \${i} = 99
    Check Log Message    ${tc.kws[0].kws[-1].kws[1].msgs[0]}    i: 99

For In Range With Start And Stop
    Check Test Case    ${TEST NAME}

For In Range With Start, Stop And Step
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For In Range Keyword    ${tc.kws[0]}    3
    Should Be For Item    ${tc.kws[0].kws[0]}    \${item} = 10
    Should Be For Item    ${tc.kws[0].kws[1]}    \${item} = 7
    Should Be For Item    ${tc.kws[0].kws[2]}    \${item} = 4

For In Range With Float Stop
    ${tc} =    Check Test Case    ${TEST NAME} 1
    Should Be For In Range Keyword    ${tc.kws[0]}    4
    Should Be For Item    ${tc.kws[0].kws[0]}    \${item} = 0.0
    Should Be For Item    ${tc.kws[0].kws[1]}    \${item} = 1.0
    Should Be For Item    ${tc.kws[0].kws[2]}    \${item} = 2.0
    Should Be For Item    ${tc.kws[0].kws[3]}    \${item} = 3.0
    ${tc} =    Check Test Case    ${TEST NAME} 2
    Should Be For In Range Keyword    ${tc.kws[0]}    3
    Should Be For Item    ${tc.kws[0].kws[0]}    \${item} = 0.0
    Should Be For Item    ${tc.kws[0].kws[1]}    \${item} = 1.0
    Should Be For Item    ${tc.kws[0].kws[2]}    \${item} = 2.0

For In Range With Float Start And Stop
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

For In Range With Float Start, Stop And Step
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For In Range Keyword    ${tc.kws[0]}    3
    Should Be For Item    ${tc.kws[0].kws[0]}    \${item} = 10.99
    Should Be For Item    ${tc.kws[0].kws[1]}    \${item} = 7.95
    Should Be For Item    ${tc.kws[0].kws[2]}    \${item} = 4.91

For In Range With Variables In Arguments
    Check Test Case    ${TEST NAME}

For In Range With Expressions
    Check Test Case    ${TEST NAME}

For In Range With Expressions Containing Floats
    Check Test Case    ${TEST NAME}

For In Range With Multiple Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For In Range Keyword    ${tc.kws[0]}    4
    Should Be For Item    ${tc.kws[0].kws[0]}    \${i} = -1, \${j} = 0, \${k} = 1
    Should Be For Item    ${tc.kws[0].kws[1]}    \${i} = 2, \${j} = 3, \${k} = 4
    Should Be For Item    ${tc.kws[0].kws[2]}    \${i} = 5, \${j} = 6, \${k} = 7
    Should Be For Item    ${tc.kws[0].kws[3]}    \${i} = 8, \${j} = 9, \${k} = 10

For In Zip
    ${tc} =    Check Test Case    ${TEST NAME}
    ${for_loop}=    Set Variable    ${tc.kws[2]}
    Should Be For In Zip Keyword    ${for_loop}    4
    Should Be For Item    ${for_loop.kws[0]}    \${item} = a, \${thing} = e
    Should Be For Item    ${for_loop.kws[1]}    \${item} = b, \${thing} = f
    Should Be For Item    ${for_loop.kws[2]}    \${item} = c, \${thing} = g
    Should Be For Item    ${for_loop.kws[3]}    \${item} = d, \${thing} = h

For In Zip With Uneven Lists
    ${tc} =    Check Test Case    ${TEST NAME}
    ${for_loop}=    Set Variable    ${tc.kws[2]}
    Should Be For In Zip Keyword    ${for_loop}    3
    Should Be For Item    ${for_loop.kws[0]}    \${item} = a, \${thing} = d
    Should Be For Item    ${for_loop.kws[1]}    \${item} = b, \${thing} = e
    Should Be For Item    ${for_loop.kws[2]}    \${item} = c, \${thing} = f

For In Zip With 3 Lists
    ${tc} =    Check Test Case    ${TEST NAME}
    ${for_loop}=    Set Variable    ${tc.kws[3]}
    Should Be For In Zip Keyword    ${for_loop}    4
    Should Be For Item    ${for_loop.kws[0]}    \${item} = a, \${thing} = e, \${stuff} = 1
    Should Be For Item    ${for_loop.kws[1]}    \${item} = b, \${thing} = f, \${stuff} = 2
    Should Be For Item    ${for_loop.kws[2]}    \${item} = c, \${thing} = g, \${stuff} = 3
    Should Be For Item    ${for_loop.kws[3]}    \${item} = d, \${thing} = h, \${stuff} = 4

For In Zip With Other Iterables
    ${tc} =    Check Test Case    ${TEST NAME}

For In Zip Rejects Strings as iterable
    ${tc} =    Check Test Case    ${TEST NAME}
    ${for_loop}=    Set Variable    ${tc.kws[1]}
    Should Be For In Zip Keyword    ${for_loop}    0
    Should Be Equal    ${for_loop.status}    FAIL

For In Zip With Non-list
    ${tc} =    Check Test Case    ${TEST NAME}
    ${for_loop}=    Set Variable    ${tc.kws[2]}
    Should Be For In Zip Keyword    ${for_loop}    0
    Should Be Equal    ${for_loop.status}    FAIL

For In Zip With Too Few Variables
    Check Test Case    ${TEST NAME}

For In Zip With Too Many Variables
    Check Test Case    ${TEST NAME}

For In Enumerate
    Check Test Case    ${TEST NAME} (with 4 items)
    Check Test Case    ${TEST NAME} (with 5 items)

For In Enumerate With 3 Variables
    Check Test Case    ${TEST NAME}

For In Enumerate With 4 Variables
    Check Test Case    ${TEST NAME}

For In Enumerate With not the right number of variables
    Check Test Case    ${TEST NAME}

For In Enumerate With Too Few Variables
    Check Test Case    ${TEST NAME}

For In Enumerate With Other Iterables
    Check Test Case    ${TEST NAME}

For Loop Of Unexpected Name
    Check Test Case    ${TEST NAME}

For In Range With Too Many Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be For In Range Keyword    ${tc.kws[0]}    0

For In Range With No Arguments
    Check Test Case    ${TEST NAME}

For In Range With Non-Number Arguments
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

For In Range With Wrong Number Of Variables
    Check Test Case    ${TEST NAME}

For In Range With Non-Existing Variables In Arguments
    Check Test Case    ${TEST NAME}

For loops are case and space insensitive
    Check Test Case    ${TEST NAME}

For word can have many colons
    Check Test Case    ${TEST NAME}

*** Keywords ***
Should Be For Keyword
    [Arguments]    ${kw}    ${subcount}
    Should Be Equal    ${kw.type}    for    Not FOR keyword
    Should Contain    ${kw.name}    IN    Not FOR keyword
    Should Be Equal As Integers    ${kw.keyword_count}    ${subcount}    Wrong number of sub keywords

Should Be For In Range Keyword
    [Arguments]    ${kw}    ${subcount}
    Should Be For Keyword    ${kw}    ${subcount}
    Should Contain    ${kw.name}    IN RANGE    Not FOR IN RANGE keyword

Should Be For In Zip Keyword
    [Arguments]    ${kw}    ${subcount}
    Should Be For Keyword    ${kw}    ${subcount}
    Should Contain    ${kw.name}    IN ZIP    Not FOR IN ZIP keyword

Should Be For Item
    [Arguments]    ${kw}    ${name}
    Should Be Equal    ${kw.type}    foritem    Not FOR item
    Should Be Equal    ${kw.name}    ${name}

Test "Simple For 2" Helper
    [Arguments]    ${kw}    ${num}
    Check Log Message    ${kw.kws[0].msgs[0]}    ${num}
    Check Log Message    ${kw.kws[1].msgs[0]}    Hello from for loop
    Should Be Equal    ${kw.kws[2].name}    BuiltIn.No Operation

Test "For With Repeat" Helper
    [Arguments]    ${kw}    ${num}
    Should Be Equal    ${kw.kws[0].name}    0x BuiltIn.Fail
    Check Log Message    ${kw.kws[1].msgs[1]}    Executed once
    Should Be Equal    ${kw.kws[2].name}    2x My UK
    Should Be Equal    ${kw.kws[2].kws[0].name}    BuiltIn.No Operation
    Check Log Message    ${kw.kws[2].kws[1].msgs[0]}    We are in My UK
    Should Be Equal    ${kw.kws[2].kws[2].name}    BuiltIn.No Operation
    Check Log Message    ${kw.kws[2].kws[3].msgs[0]}    We are in My UK
    Should Be Equal    ${kw.kws[3].name}    ${num}x BuiltIn.Log
    Check Log Message    ${kw.kws[3].msgs[1]}    Executed ${num} times
    Check Log Message    ${kw.kws[4].msgs[1]}    Executed 5 times
    Check Log Message    ${kw.kws[4].msgs[1]}    Executed 5 times
    Check Log Message    ${kw.kws[4].msgs[2]}    Executed 5 times
    Check Log Message    ${kw.kws[4].msgs[3]}    Executed 5 times
    Check Log Message    ${kw.kws[4].msgs[4]}    Executed 5 times

Check KW "My UK"
    [Arguments]    ${kw}
    Should Be Equal    ${kw.name}    My UK
    Should Be Equal    ${kw.kws[0].name}    BuiltIn.No Operation
    Check Log Message    ${kw.kws[1].msgs[0]}    We are in My UK

Check KW "My UK 2"
    [Arguments]    ${kw}    ${arg}
    Should Be Equal    ${kw.name}    My UK 2
    Check KW "My UK"    ${kw.kws[0]}
    Check Log Message    ${kw.kws[1].msgs[0]}    My UK 2 got argument "${arg}"
    Check KW "My UK"    ${kw.kws[2]}

Check KW "For In UK"
    [Arguments]    ${kw}
    Should Be Equal    ${kw.name}    For In UK
    Check Log Message    ${kw.kws[0].msgs[0]}    Not for yet
    Should Be For Keyword    ${kw.kws[1]}    2
    Check Log Message    ${kw.kws[1].kws[0].kws[0].msgs[0]}    This is for with 1
    Check KW "My UK"    ${kw.kws[1].kws[0].kws[1]}
    Check Log Message    ${kw.kws[1].kws[1].kws[0].msgs[0]}    This is for with 2
    Check KW "My UK"    ${kw.kws[1].kws[1].kws[1]}
    Check Log Message    ${kw.kws[2].msgs[0]}    Not for anymore

Check KW "For In UK With Args"
    [Arguments]    ${kw}    ${arg_count}    ${first_arg}
    Should Be Equal    ${kw.name}    For In UK With Args
    Should Be For Keyword    ${kw.kws[0]}    ${arg_count}
    Check KW "My UK 2"    ${kw.kws[0].kws[0].kws[0]}    ${first_arg}
    Should Be For Keyword    ${kw.kws[2]}    1
    Check Log Message    ${kw.kws[2].kws[0].kws[0].msgs[0]}    This for loop is executed only once

Check KW "Nested For In UK"
    [Arguments]    ${kw}    ${first_arg}
    Should Be For Keyword    ${kw.kws[0]}    1
    Check KW "For In UK"    ${kw.kws[0].kws[0].kws[0]}
    ${nested2} =    Set Variable    ${kw.kws[0].kws[0].kws[1]}
    Should Be Equal    ${nested2.name}    Nested For In UK 2
    Should Be For Keyword    ${nested2.kws[0]}    2
    Check KW "For In UK"    ${nested2.kws[0].kws[0].kws[0]}
    Check Log Message    ${nested2.kws[0].kws[0].kws[1].msgs[0]}    Got arg: ${first_arg}
    Check Log Message    ${nested2.kws[1].msgs[0]}    This ought to be enough    FAIL
