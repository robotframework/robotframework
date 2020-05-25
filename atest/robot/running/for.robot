*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for.robot
Resource          for_resource.robot

*** Test Cases ***
Simple loop
    ${tc} =    Check test case    ${TEST NAME}
    ${loop} =    Set variable    ${tc.kws[1]}
    Check log message           ${tc.kws[0].msgs[0]}             Not yet in FOR
    Should be FOR loop          ${loop}    2
    Should be loop iteration    ${loop.kws[0]}                   \${var} = one
    Check log message           ${loop.kws[0].kws[0].msgs[0]}    var: one
    Should be loop iteration    ${loop.kws[1]}                   \${var} = two
    Check log message           ${loop.kws[1].kws[0].msgs[0]}    var: two
    Check log message           ${tc.kws[2].msgs[0]}             Not in FOR anymore

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

Multiple loops in one test
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

Settings after FOR
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[0]}    1
    Check log message     ${tc.teardown.msgs[0]}    Teardown was found and eXecuted.

Invalid END usage
    Check test case    ${TEST NAME} 1
    Check test case    ${TEST NAME} 2
    Check test case    ${TEST NAME} 3
    Check test case    ${TEST NAME} 4

FOR with empty body fails
    Check test and failed loop    ${TEST NAME}

FOR without END fails
    Check test and failed loop    ${TEST NAME}

FOR without values fails
    Check test and failed loop    ${TEST NAME}

Looping over empty list variable is OK
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[0]}    0

Other iterables
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[2]}    10

FOR failing
    ${loop} =    Check test and get loop    ${TEST NAME} 1
    Should be FOR loop    ${loop}                          1                FAIL
    Check log message     ${loop.kws[0].kws[0].msgs[0]}    Hello before failing kw
    Should be equal       ${loop.kws[0].kws[0].status}     PASS
    Check log message     ${loop.kws[0].kws[1].msgs[0]}    Here we fail!    FAIL
    Should be equal       ${loop.kws[0].kws[1].status}     FAIL
    Should be equal       ${loop.kws[0].status}            FAIL
    Length should be      ${loop.kws[0].kws}               2
    ${loop} =    Check test and get loop    ${TEST NAME} 2
    Should be FOR loop    ${loop}                          4                FAIL
    Check log message     ${loop.kws[0].kws[0].msgs[0]}    Before Check
    Check log message     ${loop.kws[0].kws[2].msgs[0]}    After Check
    Length should be      ${loop.kws[0].kws}               3
    Should be equal       ${loop.kws[0].status}            PASS
    Should be equal       ${loop.kws[1].status}            PASS
    Should be equal       ${loop.kws[2].status}            PASS
    Check log message     ${loop.kws[3].kws[0].msgs[0]}    Before Check
    Check log message     ${loop.kws[3].kws[1].msgs[0]}    Failure with 4    FAIL
    Length should be      ${loop.kws[3].kws}               2
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

Nested loop in user keyword
    ${tc} =    Check test case    ${TEST NAME}
    Check kw "Nested For In UK"    ${tc.kws[0]}    foo

Loop in test and user keyword
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

No loop values
    ${tc} =    Check test case    ${TEST NAME}
    Should be FOR loop    ${tc.kws[0]}    0    FAIL

Invalid loop variable
    Check test and failed loop    ${TEST NAME} 1
    Check test and failed loop    ${TEST NAME} 2
    Check test and failed loop    ${TEST NAME} 3
    Check test and failed loop    ${TEST NAME} 4
    Check test and failed loop    ${TEST NAME} 5
    Check test and failed loop    ${TEST NAME} 6

FOR without any paramenters
    Check test case    ${TEST NAME}

FOR without variables
    Check test case    ${TEST NAME}

Loop with non-existing keyword
    Check test case    ${TEST NAME}

Loop with non-existing variable
    Check test case    ${TEST NAME}

Loop value with non-existing variable
    Check test case    ${TEST NAME}

Multiple loop variables
    ${tc} =    Check test case    ${TEST NAME}
    ${loop} =    Set Variable    ${tc.kws[0]}
    Should be FOR loop          ${loop}                          4
    Should be loop iteration    ${loop.kws[0]}                   \${x} = 1, \${y} = a
    Check log message           ${loop.kws[0].kws[0].msgs[0]}    1a
    Should be loop iteration    ${loop.kws[1]}                   \${x} = 2, \${y} = b
    Check log message           ${loop.kws[1].kws[0].msgs[0]}    2b
    Should be loop iteration    ${loop.kws[2]}                   \${x} = 3, \${y} = c
    Check log message           ${loop.kws[2].kws[0].msgs[0]}    3c
    Should be loop iteration    ${loop.kws[3]}                   \${x} = 4, \${y} = d
    Check log message           ${loop.kws[3].kws[0].msgs[0]}    4d
    ${loop} =    Set Variable    ${tc.kws[2]}
    Should be FOR loop          ${loop}           2
    Should be loop iteration    ${loop.kws[0]}    \${a} = 1, \${b} = 2, \${c} = 3, \${d} = 4, \${e} = 5
    Should be loop iteration    ${loop.kws[1]}    \${a} = 1, \${b} = 2, \${c} = 3, \${d} = 4, \${e} = 5

Wrong number of loop variables
    Check test and failed loop    ${TEST NAME} 1
    Check test and failed loop    ${TEST NAME} 2

Cut long values in iteration name
    ${tc} =         Check test case    ${TEST NAME}
    ${loop} =       Set Variable       ${tc.kws[6]}
    ${exp10} =      Set Variable       0123456789
    ${exp100} =     Evaluate           "${exp10}" * 10
    ${exp200} =     Evaluate           "${exp10}" * 20
    ${exp200+} =    Set Variable       ${exp200}...
    Should be FOR loop             ${loop}           6
    Should be loop iteration       ${loop.kws[0]}    \${var} = ${exp10}
    Should be loop iteration       ${loop.kws[1]}    \${var} = ${exp100}
    Should be loop iteration       ${loop.kws[2]}    \${var} = ${exp200}
    Should be loop iteration       ${loop.kws[3]}    \${var} = ${exp200+}
    Should be loop iteration       ${loop.kws[4]}    \${var} = ${exp200+}
    Should be loop iteration       ${loop.kws[5]}    \${var} = ${exp200+}
    ${loop} =       Set Variable       ${tc.kws[7]}
    Should be FOR loop             ${loop}           2
    Should be loop iteration       ${loop.kws[0]}    \${var1} = ${exp10}, \${var2} = ${exp100}, \${var3} = ${exp200}
    Should be loop iteration       ${loop.kws[1]}    \${var1} = ${exp200+}, \${var2} = ${exp200+}, \${var3} = ${exp200+}

Characters that are illegal in XML
    ${tc} =    Check test case    ${TEST NAME}
    Should be equal    ${tc.kws[0].kws[0].name}    \${var} = illegal:
    Should be equal    ${tc.kws[0].kws[1].name}    \${var} = more:

Header with colon is deprecated
    ${tc} =    Check test case    ${TEST NAME}
    Old style loop header is deprecated    :FOR
    ...    ${tc.kws[0].msgs[0]}    ${ERRORS[4]}

Header with colon is case and space insensitive
    ${tc} =    Check test case    ${TEST NAME}
    Old style loop header is deprecated    : f O r
    ...    ${tc.kws[0].msgs[0]}    ${ERRORS[5]}

Header can have many colons
    ${tc} =    Check test case    ${TEST NAME}
    Old style loop header is deprecated    :::f:o:r:::
    ...    ${tc.kws[0].msgs[0]}    ${ERRORS[6]}

Invalid separator
    Check test case    ${TEST NAME}

Separator is case- and space-sensitive
    Check test case    ${TEST NAME} 1
    Check test case    ${TEST NAME} 2
    Check test case    ${TEST NAME} 3
    Check test case    ${TEST NAME} 4

Escaping with backslash is deprecated
    ${tc} =    Check test case    ${TEST NAME}
    ${loop} =    Set variable    ${tc.kws[0]}
    Should be FOR loop                       ${loop}                          2
    Old style loop body is deprecated        @{loop.msgs[0:3]}                @{ERRORS[7:10]}
    Should be loop iteration                 ${loop.kws[0]}                   \${var} = one
    Check log message                        ${loop.kws[0].kws[0].msgs[0]}    var: one
    Check kw "For in UK with backslashes"    ${loop.kws[0].kws[1]}            one
    Should be loop iteration                 ${loop.kws[1]}                   \${var} = two
    Check log message                        ${loop.kws[1].kws[0].msgs[0]}    var: two
    Check kw "For in UK with backslashes"    ${loop.kws[1].kws[1]}            two
    Check log message                        ${tc.kws[1].msgs[0]}             Between for loops
    ${loop} =    Set variable    ${tc.kws[0]}
    Should be FOR loop                       ${loop}    2
    Old style loop body is deprecated        @{loop.msgs[0:3]}                @{ERRORS[10:13]}
    Should be loop iteration                 ${loop.kws[0]}                   \${var} = one
    Check log message                        ${loop.kws[0].kws[0].msgs[0]}    var: one
    Check kw "For in UK with backslashes"    ${loop.kws[0].kws[1]}            one
    Should be loop iteration                 ${loop.kws[1]}                   \${var} = two
    Check log message                        ${loop.kws[1].kws[0].msgs[0]}    var: two
    Check kw "For in UK with backslashes"    ${loop.kws[1].kws[1]}            two

END is not required when escaping with backslash
    ${tc} =    Check test case    ${TEST NAME}
    ${loop} =    Set variable    ${tc.kws[0]}
    Should be FOR loop                       ${loop}    2
    Old style loop body is deprecated        @{loop.msgs[0:3]}                @{ERRORS[13:16]}
    Should be loop iteration                 ${loop.kws[0]}                   \${var} = one
    Check log message                        ${loop.kws[0].kws[0].msgs[0]}    var: one
    Check kw "For in UK with backslashes"    ${loop.kws[0].kws[1]}            one
    Should be loop iteration                 ${loop.kws[1]}                   \${var} = two
    Check log message                        ${loop.kws[1].kws[0].msgs[0]}    var: two
    Check kw "For in UK with backslashes"    ${loop.kws[1].kws[1]}            two
    Check log message                        ${tc.kws[1].msgs[0]}             Between for loops
    ${loop} =    Set variable    ${tc.kws[0]}
    Should be FOR loop                       ${loop}    2
    Old style loop body is deprecated        @{loop.msgs[0:3]}                @{ERRORS[16:19]}
    Should be loop iteration                 ${loop.kws[0]}                   \${var} = one
    Check log message                        ${loop.kws[0].kws[0].msgs[0]}    var: one
    Check kw "For in UK with backslashes"    ${loop.kws[0].kws[1]}            one
    Should be loop iteration                 ${loop.kws[1]}                   \${var} = two
    Check log message                        ${loop.kws[1].kws[0].msgs[0]}    var: two
    Check kw "For in UK with backslashes"    ${loop.kws[1].kws[1]}            two

Header at the end of file
    Check test case    ${TEST NAME}

Old for loop in resource
    ${loop} =    Check test and get loop    ${TEST NAME}
    Old style loop header is deprecated    :FOR
    ...    ${loop.kws[0].msgs[0]}    ${ERRORS[19]}
    ...    file=old_for_in_resource.robot
    Old style loop body is deprecated
    ...    ${loop.kws[0].msgs[1]}    ${ERRORS[20]}
    ...    file=old_for_in_resource.robot

*** Keywords ***
"Variables in values" helper
    [Arguments]    ${kw}    ${num}
    Check log message    ${kw.kws[0].msgs[0]}    ${num}
    Check log message    ${kw.kws[1].msgs[0]}    Hello from for loop
    Should be equal      ${kw.kws[2].name}       BuiltIn.No Operation

Check kw "My UK"
    [Arguments]    ${kw}
    Should be equal      ${kw.name}              My UK
    Should be equal      ${kw.kws[0].name}       BuiltIn.No Operation
    Check log message    ${kw.kws[1].msgs[0]}    We are in My UK

Check kw "My UK 2"
    [Arguments]    ${kw}    ${arg}
    Should be equal      ${kw.name}              My UK 2
    Check kw "My UK"     ${kw.kws[0]}
    Check log message    ${kw.kws[1].msgs[0]}    My UK 2 got argument "${arg}"
    Check kw "My UK"     ${kw.kws[2]}

Check kw "For In UK"
    [Arguments]    ${kw}
    Should be equal       ${kw.name}                            For In UK
    Check log message     ${kw.kws[0].msgs[0]}                  Not for yet
    Should be FOR loop    ${kw.kws[1]}    2
    Check log message     ${kw.kws[1].kws[0].kws[0].msgs[0]}    This is for with 1
    Check kw "My UK"      ${kw.kws[1].kws[0].kws[1]}
    Check log message     ${kw.kws[1].kws[1].kws[0].msgs[0]}    This is for with 2
    Check kw "My UK"      ${kw.kws[1].kws[1].kws[1]}
    Check log message     ${kw.kws[2].msgs[0]}                  Not for anymore

Check kw "For In UK With Args"
    [Arguments]    ${kw}    ${arg_count}    ${first_arg}
    Should be equal       ${kw.name}                            For In UK With Args
    Should be FOR loop    ${kw.kws[0]}                          ${arg_count}
    Check kw "My UK 2"    ${kw.kws[0].kws[0].kws[0]}            ${first_arg}
    Should be FOR loop    ${kw.kws[2]}    1
    Check log message     ${kw.kws[2].kws[0].kws[0].msgs[0]}    This for loop is executed only once

Check kw "Nested For In UK"
    [Arguments]    ${kw}    ${first_arg}
    Should be FOR loop      ${kw.kws[0]}                               1                          FAIL
    Check kw "For In UK"    ${kw.kws[0].kws[0].kws[0]}
    ${nested2} =    Set Variable    ${kw.kws[0].kws[0].kws[1]}
    Should be equal         ${nested2.name}                            Nested For In UK 2
    Should be FOR loop      ${nested2.kws[0]}                          2
    Check kw "For In UK"    ${nested2.kws[0].kws[0].kws[0]}
    Check log message       ${nested2.kws[0].kws[0].kws[1].msgs[0]}    Got arg: ${first_arg}
    Check log message       ${nested2.kws[1].msgs[0]}                  This ought to be enough    FAIL

Check kw "For in UK with backslashes"
    [Arguments]    ${kw}    ${arg}
    Should be FOR loop                   ${kw.kws[0]}                         2
    Old style loop body is deprecated    ${kw.kws[0].msgs[0]}
    Should be loop iteration             ${kw.kws[0].kws[0]}                  \${x} = 1
    Check log message                    ${kw.kws[0].kws[0].kws[1].msgs[0]}   ${arg}-1
    Should be loop iteration             ${kw.kws[0].kws[1]}                  \${x} = 2
    Check log message                    ${kw.kws[0].kws[1].kws[1].msgs[0]}   ${arg}-2

Old style loop header is deprecated
    [Arguments]    ${value}    @{messages}    ${file}=for.robot
    ${path} =    Normalize path    ${DATADIR}/running/${file}
    FOR    ${msg}    IN    @{messages}
        ${error} =    Catenate
        ...    Error in file '${path}' in FOR loop starting on line *:
        ...    For loop header '${value}' is deprecated. Use 'FOR' instead.
        Check log message    ${msg}    ${error}    WARN    pattern=True
    END

Old style loop body is deprecated
    [Arguments]    @{messages}    ${file}=for.robot
    ${path} =    Normalize path    ${DATADIR}/running/${file}
    FOR    ${msg}    IN    @{messages}
        ${error} =    Catenate
        ...    Error in file '${path}' in FOR loop starting on line *:
        ...    Marking for loop body with '\\' is deprecated.
        ...    Remove markers and use 'END' instead.
        Check log message    ${msg}    ${error}    WARN    pattern=True
    END
