*** Settings ***
Suite Setup     Run And Rebot Flattened
Resource        atest_resource.robot

*** Variables ***
${FLATTEN}      --FlattenKeywords NAME:Keyword3
...             --flat name:key*others
...             --FLAT name:builtin.*
...             --flat TAG:flattenNOTkitty
...             --flatten "name:Flatten controls in keyword"
${FLATTENED}    <span class="robot-note">Content flattened.</span>
${ERROR}        [ ERROR ] Invalid value for option '--flattenkeywords': Expected 'FOR', 'WHILE', 'ITERATION', 'TAG:<pattern>' or 'NAME:<pattern>', got 'invalid'.${USAGE TIP}\n

*** Test Cases ***
Non-matching keyword is not flattened
    Should Be Equal      ${TC[0].message}     ${EMPTY}
    Should Be Equal      ${TC[0].doc}         Doc of keyword 2
    Should Have Tags     ${TC[0]}             kw2
    Should Be Equal      ${TC[0].timeout}     2 minutes
    Check Counts         ${TC[0]}             0    2
    Check Log Message    ${TC[0, 0, 0]}       2
    Check Log Message    ${TC[0, 1, 1, 0]}    1

Exact match
    Should Be Equal      ${TC[1].message}     *HTML* ${FLATTENED}
    Should Be Equal      ${TC[1].doc}         Doc of keyword 3
    Should Have Tags     ${TC[1]}             kw3
    Should Be Equal      ${TC[1].timeout}     3 minutes
    Check Counts         ${TC[1]}             3
    Check Log Message    ${TC[1, 0]}          3
    Check Log Message    ${TC[1, 1]}          2
    Check Log Message    ${TC[1, 2]}          1

Pattern match
    Should Be Equal      ${TC[2].message}     *HTML* ${FLATTENED}
    Should Be Equal      ${TC[2].doc}         ${EMPTY}
    Should Have Tags     ${TC[2]}
    Should Be Equal      ${TC[2].timeout}     ${NONE}
    Check Counts         ${TC[2]}             6
    Check Log Message    ${TC[2, 0]}          3
    Check Log Message    ${TC[2, 1]}          2
    Check Log Message    ${TC[2, 2]}          1
    Check Log Message    ${TC[2, 3]}          2
    Check Log Message    ${TC[2, 4]}          1
    Check Log Message    ${TC[2, 5]}          1

Tag match when keyword has no message
    Should Be Equal      ${TC[5].message}     *HTML* ${FLATTENED}
    Should Be Equal      ${TC[5].doc}         ${EMPTY}
    Should Have Tags     ${TC[5]}             flatten    hi
    Check Counts         ${TC[5]}             1

Tag match when keyword has message
    Should Be Equal      ${TC[6].message}     *HTML* Expected e&amp;&lt;aped failure!<hr>${FLATTENED}
    Should Be Equal      ${TC[6].doc}         Doc of flat keyword.
    Should Have Tags     ${TC[6]}             flatten    hello
    Check Counts         ${TC[6]}             1

Match full name
    Should Be Equal      ${TC[3].message}     *HTML* ${FLATTENED}
    Should Be Equal      ${TC[3].doc}         Logs the given message with the given level.
    Check Counts         ${TC[3]}             1
    Check Log Message    ${TC[3, 0]}          Flatten me too!!

Flattened in log after execution
    Should Contain       ${LOG}               "*Content flattened."

Flatten controls in keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    @{expected} =    Create List
    ...    Outside IF    Inside IF    1    Nested IF
    ...    3    2    1    BANG!
    ...    FOR: 0    1    FOR: 1    1    FOR: 2    1
    ...    WHILE: 2    1    \${i} = 1    WHILE: 1    1    \${i} = 0
    ...    AssertionError    1    finally
    ...    Inside GROUP    \${x} = Using VAR
    FOR    ${msg}    ${exp}    IN ZIP    ${tc[0].body}    ${expected}    mode=STRICT
        Check Log Message    ${msg}    ${exp}    level=IGNORE
    END

Flatten FOR
    Run Rebot    --flatten For    ${OUTFILE COPY}
    ${tc} =    Check Test Case    FOR loop
    Should Be Equal     ${tc[0].type}       FOR
    Should Be Equal     ${tc[0].message}    *HTML* ${FLATTENED}
    Check Counts        ${tc[0]}            60
    FOR    ${index}    IN RANGE    10
        Check Log Message    ${tc[0, ${index * 6 + 0}]}    index: ${index}
        Check Log Message    ${tc[0, ${index * 6 + 1}]}    3
        Check Log Message    ${tc[0, ${index * 6 + 2}]}    2
        Check Log Message    ${tc[0, ${index * 6 + 3}]}    1
        Check Log Message    ${tc[0, ${index * 6 + 4}]}    2
        Check Log Message    ${tc[0, ${index * 6 + 5}]}    1
    END

Flatten FOR iterations
    Run Rebot    --flatten ForItem    ${OUTFILE COPY}
    ${tc} =    Check Test Case    FOR loop
    Should Be Equal     ${tc[0].type}        FOR
    Should Be Equal     ${tc[0].message}     ${EMPTY}
    Check Counts        ${tc[0]}             0    10
    FOR    ${index}    IN RANGE    10
        Should Be Equal      ${tc[0, ${index}].type}       ITERATION
        Should Be Equal      ${tc[0, ${index}].message}    *HTML* ${FLATTENED}
        Check Counts         ${tc[0, ${index}]}            6
        Check Log Message    ${tc[0, ${index}, 0]}    index: ${index}
        Check Log Message    ${tc[0, ${index}, 1]}    3
        Check Log Message    ${tc[0, ${index}, 2]}    2
        Check Log Message    ${tc[0, ${index}, 3]}    1
        Check Log Message    ${tc[0, ${index}, 4]}    2
        Check Log Message    ${tc[0, ${index}, 5]}    1
    END

Flatten WHILE
    Run Rebot    --flatten WHile    ${OUTFILE COPY}
    ${tc} =    Check Test Case    WHILE loop
    Should Be Equal     ${tc[1].type}        WHILE
    Should Be Equal     ${tc[1].message}     *HTML* ${FLATTENED}
    Check Counts        ${tc[1]}             70
    FOR    ${index}    IN RANGE    10
        Check Log Message    ${tc[1, ${index * 7 + 0}]}    index: ${index}
        Check Log Message    ${tc[1, ${index * 7 + 1}]}    3
        Check Log Message    ${tc[1, ${index * 7 + 2}]}    2
        Check Log Message    ${tc[1, ${index * 7 + 3}]}    1
        Check Log Message    ${tc[1, ${index * 7 + 4}]}    2
        Check Log Message    ${tc[1, ${index * 7 + 5}]}    1
        ${i}=    Evaluate     $index + 1
        Check Log Message    ${tc[1, ${index * 7 + 6}]}    \${i} = ${i}
    END

Flatten WHILE iterations
    Run Rebot    --flatten iteration    ${OUTFILE COPY}
    ${tc} =    Check Test Case    WHILE loop
    Should Be Equal     ${tc[1].type}        WHILE
    Should Be Equal     ${tc[1].message}     ${EMPTY}
    Check Counts        ${tc[1]}             0    10
    FOR    ${index}    IN RANGE    10
        Should Be Equal      ${tc[1, ${index}].type}       ITERATION
        Should Be Equal      ${tc[1, ${index}].message}    *HTML* ${FLATTENED}
        Check Counts         ${tc[1, ${index}]}            7
        Check Log Message    ${tc[1, ${index}, 0]}         index: ${index}
        Check Log Message    ${tc[1, ${index}, 1]}         3
        Check Log Message    ${tc[1, ${index}, 2]}         2
        Check Log Message    ${tc[1, ${index}, 3]}         1
        Check Log Message    ${tc[1, ${index}, 4]}         2
        Check Log Message    ${tc[1, ${index}, 5]}         1
        ${i}=    Evaluate     $index + 1
        Check Log Message    ${tc[1, ${index}, 6]}         \${i} = ${i}
    END

Flatten with JSON
    GROUP    Run tests
        VAR    ${flatten}
        ...    --flattenkeywords name:Keyword3
        ...    --flatten-keywords tag:flattenNOTkitty
        ...    --flatten FOR
        ...    --flatten WHILE
        Run Tests Without Processing Output    ${flatten} --output output.json --log log.html    output/flatten_keywords.robot
    END
    GROUP    Check flattening in log after afecution.
        ${log} =    Get File    ${OUTDIR}/log.html
        Should Contain       ${log}               "*Content flattened."
    END
    GROUP    Run Rebot
        Copy File    ${OUTDIR}/output.json    %{TEMPDIR}/output.json
        Run Rebot    ${flatten}    %{TEMPDIR}/output.json
    END
    GROUP    Check flattening by keyword name and tags
        ${tc} =    Check Test Case    Flatten stuff
        Should Be Equal      ${tc[0].message}     ${EMPTY}
        Should Be Equal      ${tc[0].doc}         Doc of keyword 2
        Should Have Tags     ${tc[0]}             kw2
        Should Be Equal      ${tc[0].timeout}     2 minutes
        Check Counts         ${tc[0]}             0    2
        Check Log Message    ${tc[0, 0, 0]}       2
        Check Log Message    ${tc[0, 1, 1, 0]}    1
        Should Be Equal      ${tc[1].message}     *HTML* ${FLATTENED}
        Should Be Equal      ${tc[1].doc}         Doc of keyword 3
        Should Have Tags     ${tc[1]}             kw3
        Should Be Equal      ${tc[1].timeout}     3 minutes
        Check Counts         ${tc[1]}             3
        Check Log Message    ${tc[1, 0]}          3
        Check Log Message    ${tc[1, 1]}          2
        Check Log Message    ${tc[1, 2]}          1
        Should Be Equal      ${tc[5].message}     *HTML* ${FLATTENED}
        Should Be Equal      ${tc[5].doc}         ${EMPTY}
        Should Have Tags     ${tc[5]}             flatten    hi
        Check Counts         ${tc[5]}             1
        Should Be Equal      ${tc[6].message}     *HTML* Expected e&amp;&lt;aped failure!<hr>${FLATTENED}
        Should Be Equal      ${tc[6].doc}         Doc of flat keyword.
        Should Have Tags     ${tc[6]}             flatten    hello
        Check Counts         ${tc[6]}             1
    END
    GROUP    Check flattening FOR loop
        ${tc} =    Check Test Case    FOR loop
        Should Be Equal     ${tc[0].type}       FOR
        Should Be Equal     ${tc[0].message}    *HTML* ${FLATTENED}
        Check Counts        ${tc[0]}            60
        FOR    ${index}    IN RANGE    10
            Check Log Message    ${tc[0, ${index * 6 + 0}]}    index: ${index}
            Check Log Message    ${tc[0, ${index * 6 + 1}]}    3
            Check Log Message    ${tc[0, ${index * 6 + 2}]}    2
            Check Log Message    ${tc[0, ${index * 6 + 3}]}    1
            Check Log Message    ${tc[0, ${index * 6 + 4}]}    2
            Check Log Message    ${tc[0, ${index * 6 + 5}]}    1
        END
    END
    GROUP    Check flattening WHILE loop
        ${tc} =    Check Test Case    WHILE loop
        Should Be Equal     ${tc[1].type}        WHILE
        Should Be Equal     ${tc[1].message}     *HTML* ${FLATTENED}
        Check Counts        ${tc[1]}             70
        FOR    ${index}    IN RANGE    10
            Check Log Message    ${tc[1, ${index * 7 + 0}]}    index: ${index}
            Check Log Message    ${tc[1, ${index * 7 + 1}]}    3
            Check Log Message    ${tc[1, ${index * 7 + 2}]}    2
            Check Log Message    ${tc[1, ${index * 7 + 3}]}    1
            Check Log Message    ${tc[1, ${index * 7 + 4}]}    2
            Check Log Message    ${tc[1, ${index * 7 + 5}]}    1
            ${i}=    Evaluate     $index + 1
            Check Log Message    ${tc[1, ${index * 7 + 6}]}    \${i} = ${i}
        END
    END
    GROUP    Check flattening FOR and WHILE iterations
        Run Rebot    --flatten ITERATION    %{TEMPDIR}/output.json
        ${tc} =    Check Test Case    FOR loop
        Should Be Equal     ${tc[0].type}        FOR
        Should Be Equal     ${tc[0].message}     ${EMPTY}
        Check Counts        ${tc[0]}             0    10
        FOR    ${index}    IN RANGE    10
            Should Be Equal      ${tc[0, ${index}].type}       ITERATION
            Should Be Equal      ${tc[0, ${index}].message}    *HTML* ${FLATTENED}
            Check Counts         ${tc[0, ${index}]}            6
            Check Log Message    ${tc[0, ${index}, 0]}    index: ${index}
            Check Log Message    ${tc[0, ${index}, 1]}    3
            Check Log Message    ${tc[0, ${index}, 2]}    2
            Check Log Message    ${tc[0, ${index}, 3]}    1
            Check Log Message    ${tc[0, ${index}, 4]}    2
            Check Log Message    ${tc[0, ${index}, 5]}    1
        END
        ${tc} =    Check Test Case    WHILE loop
        Should Be Equal     ${tc[1].type}        WHILE
        Should Be Equal     ${tc[1].message}     ${EMPTY}
        Check Counts        ${tc[1]}             0    10
        FOR    ${index}    IN RANGE    10
            Should Be Equal      ${tc[1, ${index}].type}       ITERATION
            Should Be Equal      ${tc[1, ${index}].message}    *HTML* ${FLATTENED}
            Check Counts         ${tc[1, ${index}]}            7
            Check Log Message    ${tc[1, ${index}, 0]}         index: ${index}
            Check Log Message    ${tc[1, ${index}, 1]}         3
            Check Log Message    ${tc[1, ${index}, 2]}         2
            Check Log Message    ${tc[1, ${index}, 3]}         1
            Check Log Message    ${tc[1, ${index}, 4]}         2
            Check Log Message    ${tc[1, ${index}, 5]}         1
            ${i}=    Evaluate     $index + 1
            Check Log Message    ${tc[1, ${index}, 6]}         \${i} = ${i}
        END
    END

Invalid usage
    Run Rebot Without Processing Output    ${FLATTEN} --FlattenKeywords invalid    ${OUTFILE COPY}
    Stderr Should Be Equal To    ${ERROR}
    Run Tests Without Processing Output    ${FLATTEN} --FlattenKeywords invalid    output/flatten_keywords.robot
    Stderr Should Be Equal To    ${ERROR}

*** Keywords ***
Run And Rebot Flattened
    Run Tests Without Processing Output     ${FLATTEN} --log log.html    output/flatten_keywords.robot
    ${LOG} =    Get File    ${OUTDIR}/log.html
    Set Suite Variable    $LOG
    Copy Previous Outfile
    Run Rebot    ${FLATTEN}    ${OUTFILE COPY}
    ${TC} =    Check Test Case    Flatten stuff
    Set Suite Variable    $TC

Check Counts
    [Arguments]    ${item}    ${messages}    ${non_messages}=0
    Length Should Be    ${item.messages}        ${messages}
    Length Should Be    ${item.non_messages}    ${non_messages}
