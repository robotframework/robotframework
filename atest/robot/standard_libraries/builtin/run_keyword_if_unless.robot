*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_if_unless.robot
Resource          atest_resource.robot

*** Variable ***
${EXECUTED}       This is executed

*** Test Case ***
Run Keyword If With True Expression
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    ${EXECUTED}

Run Keyword If With False Expression
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal As Integers    ${tc.kws[0].keyword_count}    0

Run Keyword In User Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    ${EXECUTED}
    Should Be Equal As Integers    ${tc.kws[1].kws[0].keyword_count}    0

Run Keyword With ELSE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    ${EXECUTED}
    Check Log Message    ${tc.kws[3].kws[0].msgs[0]}    ${EXECUTED}

Keyword Name in ELSE as variable
    Check Test Case    ${TEST NAME}

Keyword Name in ELSE as list variable
    Check Test Case    ${TEST NAME}

Keyword Name in ELSE as non-existing variable
    [Template]    Check Test Case
    ${TEST NAME} 1
    ${TEST NAME} 2

ELSE without keyword is invalid
    [Template]    Check Test Case
    ${TEST NAME} 1
    ${TEST NAME} 2

Only first ELSE is significant
    Check Test Case    ${TEST NAME}

Run Keyword With ELSE IF
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    ${EXECUTED}

Run Keyword with ELSE IF and ELSE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    ${EXECUTED}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    ${EXECUTED}

Run Keyword with multiple ELSE IF
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    ${EXECUTED}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    ${EXECUTED}
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    ${EXECUTED}

Keyword Name in ELSE IF as variable
    Check Test Case    ${TEST NAME}

Keyword Name in ELSE IF as list variable
    Check Test Case    ${TEST NAME}

Keyword Name in ELSE IF as non-existing variable
    [Template]    Check Test Case
    ${TEST NAME} 1
    ${TEST NAME} 2
    ${TEST NAME} 3

ELSE IF without keyword is invalid
    [Template]    Check Test Case
    ${TEST NAME} 1
    ${TEST NAME} 2
    ${TEST NAME} 3
    ${TEST NAME} 4

ELSE before ELSE IF is ignored
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    ${EXECUTED}

ELSE and ELSE IF inside list arguments should be escaped
    Check Test Case    ${TEST NAME}

ELSE and ELSE IF must be upper case
    ${tc} =    Check Test Case    ${TEST NAME}
    Test ELSE (IF) Escaping    ${tc.kws[0].kws[0]}    else
    Test ELSE (IF) Escaping    ${tc.kws[1].kws[0]}    ELSE iF

ELSE and ELSE IF must be whitespace sensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Test ELSE (IF) Escaping    ${tc.kws[0].kws[0]}    EL SE
    Test ELSE (IF) Escaping    ${tc.kws[1].kws[0]}    ELSEIF

Run Keyword With Escaped ELSE and ELSE IF
    ${tc} =    Check Test Case    ${TEST NAME}
    Test ELSE (IF) Escaping    ${tc.kws[0].kws[0]}    ELSE
    Test ELSE (IF) Escaping    ${tc.kws[1].kws[0]}    ELSE IF

Run Keyword With ELSE and ELSE IF from Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Test ELSE (IF) Escaping    ${tc.kws[0].kws[0]}    ELSE
    Test ELSE (IF) Escaping    ${tc.kws[1].kws[0]}    ELSE
    Test ELSE (IF) Escaping    ${tc.kws[2].kws[0]}    ELSE IF
    Test ELSE (IF) Escaping    ${tc.kws[3].kws[0]}    ELSE IF

Run Keyword Unless With False Expression
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    ${EXECUTED}

Run Keyword Unless With True Expression
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal As Integers    ${tc.kws[0].keyword_count}    0

Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    Run Keyword In User Keyword
    Check Keyword Data    ${tc.kws[0].kws[0]}    BuiltIn.Run Keyword If    args='\${status}' == 'PASS', Log, \${message}
    Check Keyword Data    ${tc.kws[0].kws[0].kws[0]}    BuiltIn.Log    args=\${message}

*** Keywords ***
Test ELSE (IF) Escaping
    [Arguments]    ${kw}    ${else (if)}
    Length Should Be    ${kw.msgs}    2
    Check Log Message    ${kw.msgs[0]}    ${else (if)}
    Check Log Message    ${kw.msgs[1]}    ${EXECUTED}
