*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_if_unless.robot
Resource          atest_resource.robot

*** Variables ***
${EXECUTED}       This is executed

*** Test Cases ***
Run Keyword If With True Expression
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.body[0].body[0].msgs[0]}    ${EXECUTED}

Run Keyword If With False Expression
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc.body[0].body}

Run Keyword In User Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.body[0].body[0].body[0].msgs[0]}    ${EXECUTED}
    Should Be Empty    ${tc.body[1].body[0].body}

Run Keyword With ELSE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.body[1].body[0].msgs[0]}    ${EXECUTED}
    Check Log Message    ${tc.body[3].body[0].msgs[0]}    ${EXECUTED}

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
    Check Log Message    ${tc.body[1].body[0].msgs[0]}    ${EXECUTED}

Run Keyword with ELSE IF and ELSE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.body[0].body[0].msgs[0]}    ${EXECUTED}
    Check Log Message    ${tc.body[1].body[0].msgs[0]}    ${EXECUTED}

Run Keyword with multiple ELSE IF
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.body[0].body[0].msgs[0]}    ${EXECUTED}
    Check Log Message    ${tc.body[1].body[0].msgs[0]}    ${EXECUTED}
    Check Log Message    ${tc.body[2].body[0].msgs[0]}    ${EXECUTED}

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
    Check Log Message    ${tc.body[0].body[0].msgs[0]}    ${EXECUTED}

ELSE and ELSE IF inside list arguments should be escaped
    Check Test Case    ${TEST NAME}

ELSE and ELSE IF must be upper case
    ${tc} =    Check Test Case    ${TEST NAME}
    Test ELSE (IF) Escaping    ${tc.body[0].body[0]}    else
    Test ELSE (IF) Escaping    ${tc.body[1].body[0]}    ELSE iF

ELSE and ELSE IF must be whitespace sensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Test ELSE (IF) Escaping    ${tc.body[0].body[0]}    EL SE
    Test ELSE (IF) Escaping    ${tc.body[1].body[0]}    ELSEIF

Run Keyword With Escaped ELSE and ELSE IF
    ${tc} =    Check Test Case    ${TEST NAME}
    Test ELSE (IF) Escaping    ${tc.body[0].body[0]}    ELSE
    Test ELSE (IF) Escaping    ${tc.body[1].body[0]}    ELSE IF

Run Keyword With ELSE and ELSE IF from Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Test ELSE (IF) Escaping    ${tc.body[0].body[0]}    ELSE
    Test ELSE (IF) Escaping    ${tc.body[1].body[0]}    ELSE
    Test ELSE (IF) Escaping    ${tc.body[2].body[0]}    ELSE IF
    Test ELSE (IF) Escaping    ${tc.body[3].body[0]}    ELSE IF

Run Keyword Unless With False Expression
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${ERRORS[0]}                     Keyword 'BuiltIn.Run Keyword Unless' is deprecated.    WARN
    Check Log Message    ${tc.body[1].body[0]}            Keyword 'BuiltIn.Run Keyword Unless' is deprecated.    WARN
    Check Log Message    ${tc.body[1].body[1].msgs[0]}    ${EXECUTED}

Run Keyword Unless With True Expression
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${ERRORS[1]}                     Keyword 'BuiltIn.Run Keyword Unless' is deprecated.    WARN
    Check Log Message    ${tc.body[0].body[0]}            Keyword 'BuiltIn.Run Keyword Unless' is deprecated.    WARN
    Length Should Be     ${tc.body[0].body}               1

Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    Run Keyword In User Keyword
    Check Keyword Data    ${tc.body[0].body[0]}    BuiltIn.Run Keyword If    args='\${status}' == 'PASS', Log, \${message}
    Check Keyword Data    ${tc.body[0].body[0].body[0]}    BuiltIn.Log    args=\${message}

*** Keywords ***
Test ELSE (IF) Escaping
    [Arguments]    ${kw}    ${else (if)}
    Length Should Be    ${kw.msgs}    2
    Check Log Message    ${kw.msgs[0]}    ${else (if)}
    Check Log Message    ${kw.msgs[1]}    ${EXECUTED}
