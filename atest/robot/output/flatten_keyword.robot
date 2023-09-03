*** Settings ***
Suite Setup     Run And Rebot Flattened
Resource        atest_resource.robot

*** Variables ***
${FLATTEN}      --FlattenKeywords NAME:Keyword3
...             --flat name:key*others
...             --FLAT name:builtin.*
...             --flat TAG:flattenNOTkitty
...             --flatten "name:Flatten controls in keyword"
...             --log log.html
${FLAT TEXT}    _*Content flattened.*_
${FLAT HTML}    <p><i><b>Content flattened.\\x3c/b>\\x3c/i>\\x3c/p>
${ERROR}        [ ERROR ] Invalid value for option '--flattenkeywords': Expected 'FOR', 'WHILE', 'ITERATION', 'TAG:<pattern>' or 'NAME:<pattern>', got 'invalid'.${USAGE TIP}\n

*** Test Cases ***
Non-matching keyword is not flattened
    Should Be Equal    ${TC.kws[0].doc}    Doc of keyword 2
    Length Should Be    ${TC.kws[0].kws}    2
    Length Should Be    ${TC.kws[0].msgs}    0
    Check Log Message    ${TC.kws[0].kws[0].msgs[0]}    2
    Check Log Message    ${TC.kws[0].kws[1].kws[0].msgs[0]}    1

Exact match
    Should Be Equal    ${TC.kws[1].doc}    Doc of keyword 3\n\n${FLAT TEXT}
    Length Should Be    ${TC.kws[1].kws}    0
    Length Should Be    ${TC.kws[1].msgs}    3
    Check Log Message    ${TC.kws[1].msgs[0]}    3
    Check Log Message    ${TC.kws[1].msgs[1]}    2
    Check Log Message    ${TC.kws[1].msgs[2]}    1

Pattern match
    Should Be Equal    ${TC.kws[2].doc}    ${FLAT TEXT}
    Length Should Be    ${TC.kws[2].kws}    0
    Length Should Be    ${TC.kws[2].msgs}    6
    Check Log Message    ${TC.kws[2].msgs[0]}    3
    Check Log Message    ${TC.kws[2].msgs[1]}    2
    Check Log Message    ${TC.kws[2].msgs[2]}    1
    Check Log Message    ${TC.kws[2].msgs[3]}    2
    Check Log Message    ${TC.kws[2].msgs[4]}    1
    Check Log Message    ${TC.kws[2].msgs[5]}    1

Tag match when keyword has documentation
    Should Be Equal     ${TC.kws[5].doc}     Doc of flat keyword.\n\n${FLAT TEXT}
    Length Should Be    ${TC.kws[5].kws}     0
    Length Should Be    ${TC.kws[5].msgs}    1

Tag match when keyword has no documentation
    Should Be Equal     ${TC.kws[6].doc}     ${FLAT TEXT}
    Length Should Be    ${TC.kws[6].kws}     0
    Length Should Be    ${TC.kws[6].msgs}    1

Match full name
    Should Be Equal    ${TC.kws[3].doc}    Logs the given message with the given level.\n\n${FLAT TEXT}
    Length Should Be    ${TC.kws[3].kws}    0
    Length Should Be    ${TC.kws[3].msgs}    1
    Check Log Message    ${TC.kws[3].msgs[0]}    Flatten me too!!

Flattened in log after execution
    Should Contain X Times    ${LOG}    Doc of keyword 3    1
    Should Contain X Times    ${LOG}    Doc of keyword 2    1
    Should Contain X Times    ${LOG}    Doc of keyword 1    1
    Should Contain X Times    ${LOG}    ${FLAT HTML}        6
    Should Contain    ${LOG}    *<p>Doc of keyword 3\\x3c/p>\\n${FLAT HTML}
    Should Contain    ${LOG}    *${FLAT HTML}
    Should Contain    ${LOG}    *<p>Logs the given message with the given level.\\x3c/p>\\n${FLAT HTML}

Flatten controls in keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Length Should Be    ${tc.body[0].body.filter(messages=False)}    0
    Length Should Be    ${tc.body[0].body.filter(messages=True)}    23
    Length Should Be    ${tc.body[0].body}    23
    @{expected} =    Create List
    ...    Outside IF    Inside IF    1    Nested IF
    ...    3    2    1    BANG!
    ...    FOR: 0    1    FOR: 1    1    FOR: 2    1
    ...    WHILE: 2    1    \${i} = 1    WHILE: 1    1    \${i} = 0
    ...    AssertionError    1    finally
    FOR    ${msg}    ${exp}    IN ZIP    ${tc.body[0].body}    ${expected}
        Check Log Message    ${msg}    ${exp}    level=IGNORE
    END

Flatten for loops
    Run Rebot    --flatten For    ${OUTFILE COPY}
    ${tc} =    Check Test Case    For loop
    Should Be Equal    ${tc.kws[0].type}    FOR
    Should Be Equal    ${tc.kws[0].doc}    ${FLAT TEXT}
    Length Should Be    ${tc.kws[0].kws}    0
    Length Should Be    ${tc.kws[0].msgs}    60
    FOR    ${index}    IN RANGE    10
        Check Log Message    ${tc.kws[0].msgs[${index * 6 + 0}]}    index: ${index}
        Check Log Message    ${tc.kws[0].msgs[${index * 6 + 1}]}    3
        Check Log Message    ${tc.kws[0].msgs[${index * 6 + 2}]}    2
        Check Log Message    ${tc.kws[0].msgs[${index * 6 + 3}]}    1
        Check Log Message    ${tc.kws[0].msgs[${index * 6 + 4}]}    2
        Check Log Message    ${tc.kws[0].msgs[${index * 6 + 5}]}    1
    END

Flatten for loop iterations
    Run Rebot    --flatten ForItem    ${OUTFILE COPY}
    ${tc} =    Check Test Case    For loop
    Should Be Equal    ${tc.kws[0].type}    FOR
    Should Be Empty    ${tc.kws[0].doc}
    Length Should Be    ${tc.kws[0].kws}    10
    Should Be Empty    ${tc.kws[0].msgs}
    FOR    ${index}    IN RANGE    10
        Should Be Equal      ${tc.kws[0].kws[${index}].type}    ITERATION
        Should Be Equal      ${tc.kws[0].kws[${index}].doc}    ${FLAT TEXT}
        Should Be Empty      ${tc.kws[0].kws[${index}].kws}
        Length Should Be     ${tc.kws[0].kws[${index}].msgs}    6
        Check Log Message    ${tc.kws[0].kws[${index}].msgs[0]}    index: ${index}
        Check Log Message    ${tc.kws[0].kws[${index}].msgs[1]}    3
        Check Log Message    ${tc.kws[0].kws[${index}].msgs[2]}    2
        Check Log Message    ${tc.kws[0].kws[${index}].msgs[3]}    1
        Check Log Message    ${tc.kws[0].kws[${index}].msgs[4]}    2
        Check Log Message    ${tc.kws[0].kws[${index}].msgs[5]}    1
    END

Flatten while loops
    Run Rebot    --flatten WHile    ${OUTFILE COPY}
    ${tc} =    Check Test Case    WHILE loop
    Should Be Equal    ${tc.body[1].type}    WHILE
    Should Be Equal    ${tc.body[1].doc}    ${FLAT TEXT}
    Length Should Be    ${tc.body[1].kws}    0
    Length Should Be    ${tc.body[1].msgs}    70
    FOR    ${index}    IN RANGE    10
        Check Log Message    ${tc.body[1].msgs[${index * 7 + 0}]}    index: ${index}
        Check Log Message    ${tc.body[1].msgs[${index * 7 + 1}]}    3
        Check Log Message    ${tc.body[1].msgs[${index * 7 + 2}]}    2
        Check Log Message    ${tc.body[1].msgs[${index * 7 + 3}]}    1
        Check Log Message    ${tc.body[1].msgs[${index * 7 + 4}]}    2
        Check Log Message    ${tc.body[1].msgs[${index * 7 + 5}]}    1
        ${i}=    Evaluate     $index + 1
        Check Log Message    ${tc.body[1].msgs[${index * 7 + 6}]}    \${i} = ${i}
    END

Flatten while loop iterations
    Run Rebot    --flatten iteration    ${OUTFILE COPY}
    ${tc} =    Check Test Case    WHILE loop
    Should Be Equal    ${tc.body[1].type}    WHILE
    Should Be Empty    ${tc.body[1].doc}
    Length Should Be    ${tc.body[1].body}    10
    Should Be Empty    ${tc.body[1].msgs}
    FOR    ${index}    IN RANGE    10
        Should Be Equal      ${tc.kws[1].kws[${index}].type}    ITERATION
        Should Be Equal      ${tc.kws[1].kws[${index}].doc}    ${FLAT TEXT}
        Should Be Empty      ${tc.kws[1].kws[${index}].kws}
        Length Should Be     ${tc.kws[1].kws[${index}].msgs}    7
        Check Log Message    ${tc.kws[1].kws[${index}].msgs[0]}    index: ${index}
        Check Log Message    ${tc.kws[1].kws[${index}].msgs[1]}    3
        Check Log Message    ${tc.kws[1].kws[${index}].msgs[2]}    2
        Check Log Message    ${tc.kws[1].kws[${index}].msgs[3]}    1
        Check Log Message    ${tc.kws[1].kws[${index}].msgs[4]}    2
        Check Log Message    ${tc.kws[1].kws[${index}].msgs[5]}    1
        ${i}=    Evaluate     $index + 1
        Check Log Message    ${tc.kws[1].kws[${index}].msgs[6]}    \${i} = ${i}
    END

Invalid usage
    Run Rebot Without Processing Output    ${FLATTEN} --FlattenKeywords invalid   ${OUTFILE COPY}
    Stderr Should Be Equal To    ${ERROR}
    Run Tests Without Processing Output    ${FLATTEN} --FlattenKeywords invalid   output/flatten_keywords.robot
    Stderr Should Be Equal To    ${ERROR}

*** Keywords ***
Run And Rebot Flattened
    Run Tests Without Processing Output     ${FLATTEN}    output/flatten_keywords.robot
    ${LOG} =    Get File    ${OUTDIR}/log.html
    Set Suite Variable    $LOG
    Copy Previous Outfile
    Run Rebot    ${FLATTEN}    ${OUTFILE COPY}
    ${TC} =    Check Test Case    Flatten stuff
    Set Suite Variable    $TC
