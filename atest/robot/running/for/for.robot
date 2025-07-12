*** Settings ***
Suite Setup       Run Tests    --log log-tests-also-string-reprs.html    running/for/for.robot
Suite Teardown    File Should Exist    ${OUTDIR}/log-tests-also-string-reprs.html
Resource          for.resource

*** Test Cases ***
Simple loop
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message          ${tc[0, 0]}          Not yet in FOR
    Should be FOR loop         ${tc[1]}             2
    Should be FOR iteration    ${tc[1, 0]}          \${var}=one
    Check Log Message          ${tc[1, 0, 0, 0]}    var: one
    Should be FOR iteration    ${tc[1, 1]}          \${var}=two
    Check Log Message          ${tc[1, 1, 0, 0]}    var: two
    Check Log Message          ${tc[2, 0]}          Not in FOR anymore

Variables in values
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop              ${loop}       6
    "Variables in values" helper    ${loop[0]}    1
    "Variables in values" helper    ${loop[1]}    2
    "Variables in values" helper    ${loop[2]}    3
    "Variables in values" helper    ${loop[3]}    4
    "Variables in values" helper    ${loop[4]}    5
    "Variables in values" helper    ${loop[5]}    6

Indentation is not required
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be FOR loop    ${loop}    2

Values on multiple rows
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop    ${loop}             10
    Check Log Message     ${loop[0, 0, 0]}    1
    FOR    ${i}    IN RANGE    10
        Check Log Message    ${loop[${i}, 0, 0]}    ${{str($i + 1)}}
    END
    # Sanity check
    Check Log Message    ${loop[0, 0, 0]}    1
    Check Log Message    ${loop[4, 0, 0]}    5
    Check Log Message    ${loop[9, 0, 0]}    10

Keyword arguments on multiple rows
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop    ${loop}             2
    Check Log Message     ${loop[0, 1, 0]}    1 2 3 4 5 6 7 one
    Check Log Message     ${loop[1, 1, 0]}    1 2 3 4 5 6 7 two

Multiple loops in a test
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be FOR loop    ${tc[0]}             2
    Check Log Message     ${tc[0, 0, 0, 0]}    In first loop with "foo"
    Check Log Message     ${tc[0, 1, 0, 0]}    In first loop with "bar"
    Should be FOR loop    ${tc[1]}             1
    Check kw "My UK 2"    ${tc[1, 0, 0]}       Hello, world!
    Check Log Message     ${tc[2, 0]}          Outside loop
    Should be FOR loop    ${tc[3]}             2
    Check Log Message     ${tc[3, 0, 0, 0]}    Third loop
    Check Log Message     ${tc[3, 0, 2, 0]}    Value: a
    Check Log Message     ${tc[3, 1, 0, 0]}    Third loop
    Check Log Message     ${tc[3, 1, 2, 0]}    Value: b
    Check Log Message     ${tc[4, 0]}          The End

Nested loop syntax
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be FOR loop    ${tc[0]}                   3
    Should be FOR loop    ${tc[0, 0, 1]}             3
    Check Log Message     ${tc[0, 0, 0, 0]}          1 in
    Check Log Message     ${tc[0, 0, 1, 0, 0, 0]}    values 1 a
    Check Log Message     ${tc[0, 0, 1, 1, 0, 0]}    values 1 b
    Check Log Message     ${tc[0, 0, 1, 2, 0, 0]}    values 1 c
    Check Log Message     ${tc[0, 0, 2, 0]}          1 out
    Check Log Message     ${tc[0, 1, 0, 0]}          2 in
    Check Log Message     ${tc[0, 1, 1, 0, 0, 0]}    values 2 a
    Check Log Message     ${tc[0, 1, 1, 1, 0, 0]}    values 2 b
    Check Log Message     ${tc[0, 1, 1, 2, 0, 0]}    values 2 c
    Check Log Message     ${tc[0, 1, 2, 0]}          2 out
    Check Log Message     ${tc[0, 2, 0, 0]}          3 in
    Check Log Message     ${tc[0, 2, 1, 0, 0, 0]}    values 3 a
    Check Log Message     ${tc[0, 2, 1, 1, 0, 0]}    values 3 b
    Check Log Message     ${tc[0, 2, 1, 2, 0, 0]}    values 3 c
    Check Log Message     ${tc[0, 2, 2, 0]}          3 out
    Check Log Message     ${tc[1, 0]}                The End

Multiple loops in a loop
    Check Test Case    ${TEST NAME}

Deeply nested loops
    Check Test Case    ${TEST NAME}

Settings after FOR
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be FOR loop    ${tc[0]}    1
    Check Log Message     ${tc.teardown[0]}    Teardown was found and eXecuted.

Looping over empty list variable is OK
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be FOR loop         ${tc[0]}          1               NOT RUN
    Should be FOR iteration    ${tc[0, 0]}       \${var}=
    Check keyword data         ${tc[0, 0, 0]}    BuiltIn.Fail    args=Not executed    status=NOT RUN

Other iterables
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be FOR loop    ${tc[2]}    10

Failure inside FOR
    ${loop} =    Check test and get loop    ${TEST NAME} 1
    Should be FOR loop    ${loop}                 1                FAIL
    Check Log Message     ${loop[0, 0, 0]}        Hello before failing kw
    Should Be Equal       ${loop[0, 0].status}    PASS
    Check Log Message     ${loop[0, 1, 0]}        Here we fail!    FAIL
    Should Be Equal       ${loop[0, 1].status}    FAIL
    Should Be Equal       ${loop[0, 2].status}    NOT RUN
    Should Be Equal       ${loop[0].status}       FAIL
    Length Should Be      ${loop[0].body}         3
    ${loop} =    Check test and get loop    ${TEST NAME} 2
    Should be FOR loop    ${loop}                 4                FAIL
    Check Log Message     ${loop[0, 0, 0]}        Before Check
    Check Log Message     ${loop[0, 2, 0]}        After Check
    Length Should Be      ${loop[0].body}         3
    Should Be Equal       ${loop[0].status}       PASS
    Should Be Equal       ${loop[1].status}       PASS
    Should Be Equal       ${loop[2].status}       PASS
    Check Log Message     ${loop[3, 0, 0]}        Before Check
    Check Log Message     ${loop[3, 1, 0]}        Failure with <4>    FAIL
    Should Be Equal       ${loop[3, 2].status}    NOT RUN
    Length Should Be      ${loop[3].body}         3
    Should Be Equal       ${loop[3].status}       FAIL

Loop with user keywords
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop    ${loop}    2
    Check kw "My UK"      ${loop[0, 0]}
    Check kw "My UK 2"    ${loop[0, 1]}    foo
    Check kw "My UK"      ${loop[1, 0]}
    Check kw "My UK 2"    ${loop[1, 1]}    bar

Loop with failures in user keywords
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be FOR loop    ${tc[0]}    2    FAIL

Loop in user keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check kw "For In UK"              ${tc[0]}
    Check kw "For In UK with Args"    ${tc[1]}    4    one

Keyword with loop calling other keywords with loops
    ${tc} =    Check Test Case    ${TEST NAME}
    Check kw "Nested For In UK"    ${tc[0]}    foo

Test with loop calling keywords with loops
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be FOR loop                ${loop}          1      FAIL
    Check kw "For In UK"              ${loop[0, 0]}
    Check kw "For In UK with Args"    ${loop[0, 1]}    2      one
    Check kw "Nested For In UK"       ${loop[0, 2]}    one

Loop variables is available after loop
    Check Test Case    ${TEST NAME}

Assign inside loop
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop    ${loop}    2
    Check Log Message     ${loop[0, 0, 0]}    \${v1} = v1
    Check Log Message     ${loop[0, 1, 0]}    \${v2} = v2
    Check Log Message     ${loop[0, 1, 1]}    \${v3} = vY
    Check Log Message     ${loop[0, 2, 0]}    \@{list} = [ v1 | v2 | vY | Y ]
    Check Log Message     ${loop[1, 0, 0]}    \${v1} = v1
    Check Log Message     ${loop[1, 1, 0]}    \${v2} = v2
    Check Log Message     ${loop[1, 1, 1]}    \${v3} = vZ
    Check Log Message     ${loop[1, 2, 0]}    \@{list} = [ v1 | v2 | vZ | Z ]

Invalid assign inside loop
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be FOR loop    ${tc[0]}    1    FAIL

Loop with non-existing keyword
    Check Test Case    ${TEST NAME}

Loop with non-existing variable
    Check Test Case    ${TEST NAME}

Loop value with non-existing variable
    Check Test Case    ${TEST NAME}

Multiple loop variables
    ${tc} =    Check Test Case    ${TEST NAME}
    ${loop} =    Set Variable     ${tc[0]}
    Should be FOR loop            ${loop}             4
    Should be FOR iteration       ${loop[0]}          \${x}=1    \${y}=a
    Check Log Message             ${loop[0, 0, 0]}    1a
    Should be FOR iteration       ${loop[1]}          \${x}=2    \${y}=b
    Check Log Message             ${loop[1, 0, 0]}    2b
    Should be FOR iteration       ${loop[2]}          \${x}=3    \${y}=c
    Check Log Message             ${loop[2, 0, 0]}    3c
    Should be FOR iteration       ${loop[3]}          \${x}=4    \${y}=d
    Check Log Message             ${loop[3, 0, 0]}    4d
    ${loop} =    Set Variable     ${tc[2]}
    Should be FOR loop            ${loop}       2
    Should be FOR iteration       ${loop[0]}    \${a}=1    \${b}=2    \${c}=3    \${d}=4    \${e}=5
    Should be FOR iteration       ${loop[1]}    \${a}=1    \${b}=2    \${c}=3    \${d}=4    \${e}=5

Wrong number of loop variables
    Check test and failed loop    ${TEST NAME} 1
    Check test and failed loop    ${TEST NAME} 2

Cut long iteration variable values
    ${tc} =         Check Test Case    ${TEST NAME}
    ${loop} =       Set Variable       ${tc[6]}
    ${exp10} =      Set Variable       0123456789
    ${exp100} =     Evaluate           "${exp10}" * 10
    ${exp200} =     Evaluate           "${exp10}" * 20
    ${exp200+} =    Set Variable       ${exp200}...
    Should be FOR loop            ${loop}       6
    Should be FOR iteration       ${loop[0]}    \${var}=${exp10}
    Should be FOR iteration       ${loop[1]}    \${var}=${exp100}
    Should be FOR iteration       ${loop[2]}    \${var}=${exp200}
    Should be FOR iteration       ${loop[3]}    \${var}=${exp200+}
    Should be FOR iteration       ${loop[4]}    \${var}=${exp200+}
    Should be FOR iteration       ${loop[5]}    \${var}=${exp200+}
    ${loop} =    Set Variable     ${tc[7]}
    Should be FOR loop            ${loop}       2
    Should be FOR iteration       ${loop[0]}    \${var1}=${exp10}      \${var2}=${exp100}     \${var3}=${exp200}
    Should be FOR iteration       ${loop[1]}    \${var1}=${exp200+}    \${var2}=${exp200+}    \${var3}=${exp200+}

Characters that are illegal in XML
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be FOR iteration       ${tc[0, 0]}    \${var}=illegal:
    Should be FOR iteration       ${tc[0, 1]}    \${var}=more:

Old :FOR syntax is not supported
    Check Test Case    ${TESTNAME}

Escaping with backslash is not supported
    Check Test Case    ${TESTNAME}

FOR is case and space sensitive
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Invalid END usage
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Empty body
    Check test and failed loop    ${TEST NAME}

No END
    Check test and failed loop    ${TEST NAME}

Invalid END
    Check test and failed loop    ${TEST NAME}

No loop values
    Check test and failed loop    ${TEST NAME}

No loop variables
    Check test and failed loop    ${TEST NAME}

Invalid loop variable
    Check test and failed loop    ${TEST NAME} 1
    Check test and failed loop    ${TEST NAME} 2
    Check test and failed loop    ${TEST NAME} 3
    Check test and failed loop    ${TEST NAME} 4
    Check test and failed loop    ${TEST NAME} 5
    Check test and failed loop    ${TEST NAME} 6

Invalid separator
    Check Test Case    ${TEST NAME}

Separator is case- and space-sensitive
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3
    Check Test Case    ${TEST NAME} 4

FOR without any paramenters
    Check Test Case    ${TESTNAME}

Syntax error in nested loop
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Unexecuted
    ${tc} =    Check Test Case    ${TESTNAME}
    Should be FOR loop         ${tc[1, 0, 0]}       1         NOT RUN
    Should be FOR iteration    ${tc[1, 0, 0, 0]}    \${x}=    \${y}=
    Should be FOR loop         ${tc[5]}             1         NOT RUN
    Should be FOR iteration    ${tc[5, 0]}          \${x}=    \${y}=

Header at the end of file
    Check Test Case    ${TESTNAME}

*** Keywords ***
"Variables in values" helper
    [Arguments]    ${kw}    ${num}
    Check Log Message    ${kw[0, 0]}           ${num}
    Check Log Message    ${kw[1, 0]}           Hello from for loop
    Should Be Equal      ${kw[2].full_name}    BuiltIn.No Operation

Check kw "My UK"
    [Arguments]    ${kw}
    Should Be Equal      ${kw.full_name}       My UK
    Should Be Equal      ${kw[0].full_name}    BuiltIn.No Operation
    Check Log Message    ${kw[1, 0]}           We are in My UK

Check kw "My UK 2"
    [Arguments]    ${kw}    ${arg}
    Should Be Equal      ${kw.full_name}       My UK 2
    Check kw "My UK"     ${kw[0]}
    Check Log Message    ${kw[1, 0]}           My UK 2 got argument "${arg}"
    Check kw "My UK"     ${kw[2]}

Check kw "For In UK"
    [Arguments]    ${kw}
    Should Be Equal       ${kw.full_name}      For In UK
    Check Log Message     ${kw[0, 0]}          Not for yet
    Should be FOR loop    ${kw[1]}             2
    Check Log Message     ${kw[1, 0, 0, 0]}    This is for with 1
    Check kw "My UK"      ${kw[1, 0, 1]}
    Check Log Message     ${kw[1, 1, 0, 0]}    This is for with 2
    Check kw "My UK"      ${kw[1, 1, 1]}
    Check Log Message     ${kw[2, 0]}          Not for anymore

Check kw "For In UK With Args"
    [Arguments]    ${kw}    ${arg_count}    ${first_arg}
    Should Be Equal       ${kw.full_name}      For In UK With Args
    Should be FOR loop    ${kw[0]}             ${arg_count}
    Check kw "My UK 2"    ${kw[0, 0, 0]}       ${first_arg}
    Should be FOR loop    ${kw[2]}    1
    Check Log Message     ${kw[2, 0, 0, 0]}    This for loop is executed only once

Check kw "Nested For In UK"
    [Arguments]    ${kw}    ${first_arg}
    Should be FOR loop      ${kw[0]}                  1                          FAIL
    Check kw "For In UK"    ${kw[0, 0, 0]}
    ${nested2} =    Set Variable    ${kw[0, 0, 1]}
    Should Be Equal         ${nested2.full_name}      Nested For In UK 2
    Should be FOR loop      ${nested2[0]}             2
    Check kw "For In UK"    ${nested2[0, 0, 0]}
    Check Log Message       ${nested2[0, 0, 1, 0]}    Got arg: ${first_arg}
    Check Log Message       ${nested2[1, 0]}          This ought to be enough    FAIL
