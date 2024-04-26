*** Settings ***
Suite Setup       Run Tests    --log log-tests-also-string-reprs.html    running/for/for.robot
Suite Teardown    File Should Exist    ${OUTDIR}/log-tests-also-string-reprs.html
Resource          for.resource

*** Test Cases ***
Simple loop
    ${tc} =    Check test case    ${TEST NAME}
    ${loop} =    Set variable    ${tc.body[1]}
    Check log message          ${tc.body[0].msgs[0]}              Not yet in FOR
    Should be FOR loop         ${loop}    2
    Should be FOR iteration    ${loop.body[0]}                    \${var}=one
    Check log message          ${loop.body[0].body[0].msgs[0]}    var: one
    Should be FOR iteration    ${loop.body[1]}                    \${var}=two
    Check log message          ${loop.body[1].body[0].msgs[0]}    var: two
    Check log message          ${tc.body[2].body[0]}              Not in FOR anymore

Variables in values
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop              ${loop}    6
    "Variables in values" helper    ${loop.kws[0]}    1
    "Variables in values" helper    ${loop.kws[1]}    2
    "Variables in values" helper    ${loop.kws[2]}    3
    "Variables in values" helper    ${loop.kws[3]}    4
    "Variables in values" helper    ${loop.kws[4]}    5
    "Variables in values" helper    ${loop.kws[5]}    6

Indentation is not required
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be FOR loop    ${loop}    2

Values on multiple rows
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop    ${loop}    10
    Check log message     ${loop.kws[0].kws[0].msgs[0]}    1
    FOR    ${i}    IN RANGE    10
        Check log message    ${loop.kws[${i}].kws[0].msgs[0]}    ${{str($i + 1)}}
    END
    # Sanity check
    Check log message    ${loop.kws[0].kws[0].msgs[0]}    1
    Check log message    ${loop.kws[4].kws[0].msgs[0]}    5
    Check log message    ${loop.kws[9].kws[0].msgs[0]}    10

Keyword arguments on multiple rows
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop    ${loop}    2
    Check log message     ${loop.kws[0].kws[1].msgs[0]}    1 2 3 4 5 6 7 one
    Check log message     ${loop.kws[1].kws[1].msgs[0]}    1 2 3 4 5 6 7 two

Multiple loops in a test
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[0]}                          2
    Check log message     ${tc.kws[0].kws[0].kws[0].msgs[0]}    In first loop with "foo"
    Check log message     ${tc.kws[0].kws[1].kws[0].msgs[0]}    In first loop with "bar"
    Should be FOR loop    ${tc.kws[1]}                          1
    Check kw "My UK 2"    ${tc.kws[1].kws[0].kws[0]}            Hello, world!
    Check log message     ${tc.kws[2].msgs[0]}                  Outside loop
    Should be FOR loop    ${tc.kws[3]}                          2
    Check log message     ${tc.kws[3].kws[0].kws[0].msgs[0]}    Third loop
    Check log message     ${tc.kws[3].kws[0].kws[2].msgs[0]}    Value: a
    Check log message     ${tc.kws[3].kws[1].kws[0].msgs[0]}    Third loop
    Check log message     ${tc.kws[3].kws[1].kws[2].msgs[0]}    Value: b
    Check log message     ${tc.kws[4].msgs[0]}                  The End

Nested loop syntax
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[0]}                          3
    Should be FOR loop    ${tc.kws[0].kws[0].kws[1]}            3
    Check log message     ${tc.kws[0].kws[0].kws[0].msgs[0]}                  1 in
    Check log message     ${tc.kws[0].kws[0].kws[1].kws[0].kws[0].msgs[0]}    values 1 a
    Check log message     ${tc.kws[0].kws[0].kws[1].kws[1].kws[0].msgs[0]}    values 1 b
    Check log message     ${tc.kws[0].kws[0].kws[1].kws[2].kws[0].msgs[0]}    values 1 c
    Check log message     ${tc.kws[0].kws[0].kws[2].msgs[0]}                  1 out
    Check log message     ${tc.kws[0].kws[1].kws[0].msgs[0]}                  2 in
    Check log message     ${tc.kws[0].kws[1].kws[1].kws[0].kws[0].msgs[0]}    values 2 a
    Check log message     ${tc.kws[0].kws[1].kws[1].kws[1].kws[0].msgs[0]}    values 2 b
    Check log message     ${tc.kws[0].kws[1].kws[1].kws[2].kws[0].msgs[0]}    values 2 c
    Check log message     ${tc.kws[0].kws[1].kws[2].msgs[0]}                  2 out
    Check log message     ${tc.kws[0].kws[2].kws[0].msgs[0]}                  3 in
    Check log message     ${tc.kws[0].kws[2].kws[1].kws[0].kws[0].msgs[0]}    values 3 a
    Check log message     ${tc.kws[0].kws[2].kws[1].kws[1].kws[0].msgs[0]}    values 3 b
    Check log message     ${tc.kws[0].kws[2].kws[1].kws[2].kws[0].msgs[0]}    values 3 c
    Check log message     ${tc.kws[0].kws[2].kws[2].msgs[0]}                  3 out
    Check log message     ${tc.kws[1].msgs[0]}                                The End

Multiple loops in a loop
    Check test case    ${TEST NAME}

Deeply nested loops
    Check test case    ${TEST NAME}

Settings after FOR
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[0]}    1
    Check log message     ${tc.teardown.msgs[0]}    Teardown was found and eXecuted.

Looping over empty list variable is OK
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop         ${tc.kws[0]}                     1               NOT RUN
    Should be FOR iteration    ${tc.body[0].body[0]}            \${var}=
    Check keyword data         ${tc.body[0].body[0].body[0]}    BuiltIn.Fail    args=Not executed    status=NOT RUN

Other iterables
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[2]}    10

Failure inside FOR
    ${loop} =    Check test and get loop    ${TEST NAME} 1
    Should be FOR loop    ${loop}                          1                FAIL
    Check log message     ${loop.kws[0].kws[0].msgs[0]}    Hello before failing kw
    Should be equal       ${loop.kws[0].kws[0].status}     PASS
    Check log message     ${loop.kws[0].kws[1].msgs[0]}    Here we fail!    FAIL
    Should be equal       ${loop.kws[0].kws[1].status}     FAIL
    Should be equal       ${loop.kws[0].kws[2].status}     NOT RUN
    Should be equal       ${loop.kws[0].status}            FAIL
    Length should be      ${loop.kws[0].kws}               3
    ${loop} =    Check test and get loop    ${TEST NAME} 2
    Should be FOR loop    ${loop}                          4                FAIL
    Check log message     ${loop.kws[0].kws[0].msgs[0]}    Before Check
    Check log message     ${loop.kws[0].kws[2].msgs[0]}    After Check
    Length should be      ${loop.kws[0].kws}               3
    Should be equal       ${loop.kws[0].status}            PASS
    Should be equal       ${loop.kws[1].status}            PASS
    Should be equal       ${loop.kws[2].status}            PASS
    Check log message     ${loop.kws[3].kws[0].msgs[0]}    Before Check
    Check log message     ${loop.kws[3].kws[1].msgs[0]}    Failure with <4>    FAIL
    Should be equal       ${loop.kws[3].kws[2].status}     NOT RUN
    Length should be      ${loop.kws[3].kws}               3
    Should be equal       ${loop.kws[3].status}            FAIL

Loop with user keywords
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop    ${loop}    2
    Check kw "My UK"      ${loop.kws[0].kws[0]}
    Check kw "My UK 2"    ${loop.kws[0].kws[1]}    foo
    Check kw "My UK"      ${loop.kws[1].kws[0]}
    Check kw "My UK 2"    ${loop.kws[1].kws[1]}    bar

Loop with failures in user keywords
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[0]}    2    FAIL

Loop in user keyword
    ${tc} =    Check test case    ${TEST NAME}
    Check kw "For In UK"              ${tc.kws[0]}
    Check kw "For In UK with Args"    ${tc.kws[1]}    4    one

Keyword with loop calling other keywords with loops
    ${tc} =    Check test case    ${TEST NAME}
    Check kw "Nested For In UK"    ${tc.kws[0]}    foo

Test with loop calling keywords with loops
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be FOR loop                ${loop}                  1      FAIL
    Check kw "For In UK"              ${loop.kws[0].kws[0]}
    Check kw "For In UK with Args"    ${loop.kws[0].kws[1]}    2      one
    Check kw "Nested For In UK"       ${loop.kws[0].kws[2]}    one

Loop variables is available after loop
    Check test case    ${TEST NAME}

Assign inside loop
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be FOR loop    ${loop}    2
    Check log message     ${loop.kws[0].kws[0].msgs[0]}    \${v1} = v1
    Check log message     ${loop.kws[0].kws[1].msgs[0]}    \${v2} = v2
    Check log message     ${loop.kws[0].kws[1].msgs[1]}    \${v3} = vY
    Check log message     ${loop.kws[0].kws[2].msgs[0]}    \@{list} = [ v1 | v2 | vY | Y ]
    Check log message     ${loop.kws[1].kws[0].msgs[0]}    \${v1} = v1
    Check log message     ${loop.kws[1].kws[1].msgs[0]}    \${v2} = v2
    Check log message     ${loop.kws[1].kws[1].msgs[1]}    \${v3} = vZ
    Check log message     ${loop.kws[1].kws[2].msgs[0]}    \@{list} = [ v1 | v2 | vZ | Z ]

Invalid assign inside loop
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[0]}    1    FAIL

Loop with non-existing keyword
    Check test case    ${TEST NAME}

Loop with non-existing variable
    Check test case    ${TEST NAME}

Loop value with non-existing variable
    Check test case    ${TEST NAME}

Multiple loop variables
    ${tc} =    Check Test Case    ${TEST NAME}
    ${loop} =    Set Variable     ${tc.body[0]}
    Should be FOR loop            ${loop}                            4
    Should be FOR iteration       ${loop.body[0]}                    \${x}=1    \${y}=a
    Check log message             ${loop.body[0].body[0].msgs[0]}    1a
    Should be FOR iteration       ${loop.body[1]}                    \${x}=2    \${y}=b
    Check log message             ${loop.body[1].body[0].msgs[0]}    2b
    Should be FOR iteration       ${loop.body[2]}                    \${x}=3    \${y}=c
    Check log message             ${loop.body[2].body[0].msgs[0]}    3c
    Should be FOR iteration       ${loop.body[3]}                    \${x}=4    \${y}=d
    Check log message             ${loop.body[3].body[0].msgs[0]}    4d
    ${loop} =    Set Variable     ${tc.body[2]}
    Should be FOR loop            ${loop}            2
    Should be FOR iteration       ${loop.body[0]}    \${a}=1    \${b}=2    \${c}=3    \${d}=4    \${e}=5
    Should be FOR iteration       ${loop.body[1]}    \${a}=1    \${b}=2    \${c}=3    \${d}=4    \${e}=5

Wrong number of loop variables
    Check test and failed loop    ${TEST NAME} 1
    Check test and failed loop    ${TEST NAME} 2

Cut long iteration variable values
    ${tc} =         Check test case    ${TEST NAME}
    ${loop} =       Set Variable       ${tc.body[6]}
    ${exp10} =      Set Variable       0123456789
    ${exp100} =     Evaluate           "${exp10}" * 10
    ${exp200} =     Evaluate           "${exp10}" * 20
    ${exp200+} =    Set Variable       ${exp200}...
    Should be FOR loop            ${loop}            6
    Should be FOR iteration       ${loop.body[0]}    \${var}=${exp10}
    Should be FOR iteration       ${loop.body[1]}    \${var}=${exp100}
    Should be FOR iteration       ${loop.body[2]}    \${var}=${exp200}
    Should be FOR iteration       ${loop.body[3]}    \${var}=${exp200+}
    Should be FOR iteration       ${loop.body[4]}    \${var}=${exp200+}
    Should be FOR iteration       ${loop.body[5]}    \${var}=${exp200+}
    ${loop} =    Set Variable     ${tc.body[7]}
    Should be FOR loop            ${loop}            2
    Should be FOR iteration       ${loop.body[0]}    \${var1}=${exp10}      \${var2}=${exp100}     \${var3}=${exp200}
    Should be FOR iteration       ${loop.body[1]}    \${var1}=${exp200+}    \${var2}=${exp200+}    \${var3}=${exp200+}

Characters that are illegal in XML
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR iteration       ${tc.body[0].body[0]}    \${var}=illegal:
    Should be FOR iteration       ${tc.body[0].body[1]}    \${var}=more:

Old :FOR syntax is not supported
    Check Test Case    ${TESTNAME}

Escaping with backslash is not supported
    Check Test Case    ${TESTNAME}

FOR is case and space sensitive
    Check test case    ${TEST NAME} 1
    Check test case    ${TEST NAME} 2

Invalid END usage
    Check test case    ${TEST NAME} 1
    Check test case    ${TEST NAME} 2

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
    Check test case    ${TEST NAME}

Separator is case- and space-sensitive
    Check test case    ${TEST NAME} 1
    Check test case    ${TEST NAME} 2
    Check test case    ${TEST NAME} 3
    Check test case    ${TEST NAME} 4

FOR without any paramenters
    Check Test Case    ${TESTNAME}

Syntax error in nested loop
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Unexecuted
    ${tc} =    Check Test Case    ${TESTNAME}
    Should be FOR loop         ${tc.body[1].body[0].body[0]}            1         NOT RUN
    Should be FOR iteration    ${tc.body[1].body[0].body[0].body[0]}    \${x}=    \${y}=
    Should be FOR loop         ${tc.body[5]}                            1         NOT RUN
    Should be FOR iteration    ${tc.body[5].body[0]}                    \${x}=    \${y}=

Header at the end of file
    Check Test Case    ${TESTNAME}

*** Keywords ***
"Variables in values" helper
    [Arguments]    ${kw}    ${num}
    Check log message    ${kw.kws[0].msgs[0]}         ${num}
    Check log message    ${kw.kws[1].msgs[0]}         Hello from for loop
    Should be equal      ${kw.kws[2].full_name}       BuiltIn.No Operation

Check kw "My UK"
    [Arguments]    ${kw}
    Should be equal      ${kw.full_name}              My UK
    Should be equal      ${kw.kws[0].full_name}       BuiltIn.No Operation
    Check log message    ${kw.kws[1].msgs[0]}         We are in My UK

Check kw "My UK 2"
    [Arguments]    ${kw}    ${arg}
    Should be equal      ${kw.full_name}              My UK 2
    Check kw "My UK"     ${kw.kws[0]}
    Check log message    ${kw.kws[1].msgs[0]}         My UK 2 got argument "${arg}"
    Check kw "My UK"     ${kw.kws[2]}

Check kw "For In UK"
    [Arguments]    ${kw}
    Should be equal       ${kw.full_name}                       For In UK
    Check log message     ${kw.kws[0].msgs[0]}                  Not for yet
    Should be FOR loop    ${kw.kws[1]}    2
    Check log message     ${kw.kws[1].kws[0].kws[0].msgs[0]}    This is for with 1
    Check kw "My UK"      ${kw.kws[1].kws[0].kws[1]}
    Check log message     ${kw.kws[1].kws[1].kws[0].msgs[0]}    This is for with 2
    Check kw "My UK"      ${kw.kws[1].kws[1].kws[1]}
    Check log message     ${kw.kws[2].msgs[0]}                  Not for anymore

Check kw "For In UK With Args"
    [Arguments]    ${kw}    ${arg_count}    ${first_arg}
    Should be equal       ${kw.full_name}                       For In UK With Args
    Should be FOR loop    ${kw.kws[0]}                          ${arg_count}
    Check kw "My UK 2"    ${kw.kws[0].kws[0].kws[0]}            ${first_arg}
    Should be FOR loop    ${kw.kws[2]}    1
    Check log message     ${kw.kws[2].kws[0].kws[0].msgs[0]}    This for loop is executed only once

Check kw "Nested For In UK"
    [Arguments]    ${kw}    ${first_arg}
    Should be FOR loop      ${kw.kws[0]}                               1                          FAIL
    Check kw "For In UK"    ${kw.kws[0].kws[0].kws[0]}
    ${nested2} =    Set Variable    ${kw.kws[0].kws[0].kws[1]}
    Should be equal         ${nested2.full_name}                       Nested For In UK 2
    Should be FOR loop      ${nested2.kws[0]}                          2
    Check kw "For In UK"    ${nested2.kws[0].kws[0].kws[0]}
    Check log message       ${nested2.kws[0].kws[0].kws[1].msgs[0]}    Got arg: ${first_arg}
    Check log message       ${nested2.kws[1].msgs[0]}                  This ought to be enough    FAIL
