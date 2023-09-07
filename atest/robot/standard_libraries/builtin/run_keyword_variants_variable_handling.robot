*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_variants_variable_handling.robot
Resource          atest_resource.robot

*** Test Cases ***
Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}                                 BuiltIn.Run Keyword    args=My UK, Log, \${OBJECT}
    Check Keyword Data    ${tc.kws[0].kws[0]}                          My UK    args=Log, \${OBJECT}
    Check Keyword Data    ${tc.kws[0].kws[0].kws[0]}                   BuiltIn.Run Keyword    args=\${name}, \@{args}
    Check Keyword Data    ${tc.kws[0].kws[0].kws[0].kws[0]}            BuiltIn.Log    args=\@{args}
    Check Log Message     ${tc.kws[0].kws[0].kws[0].kws[0].msgs[0]}    Robot
    Check Keyword Data    ${tc.kws[0].kws[0].kws[1].kws[0]}            BuiltIn.Log    args=\${args}[0]
    Check Log Message     ${tc.kws[0].kws[0].kws[1].kws[0].msgs[0]}    Robot

Run Keyword When Keyword and Arguments Are in List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0].kws[0]}    \\Log Many    args=c:\\\\temp\\\\foo, \\\${notvar}
    Check Keyword Data    ${tc.kws[1].kws[0]}    \\Log Many    args=\\\${notvar}

Run Keyword With Empty List Variable
    Check Test Case    ${TEST NAME}

Run Keyword With Multiple Empty List Variables
    Check Test Case    ${TEST NAME}

Run Keyword If When Arguments are In Multiple List
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Arguments And Messages    ${tc}

Run Keyword When Arguments are Not In First Lists
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Arguments And Messages    ${tc}

Run Keyword When Keyword And Arguments In Scalar After Empty Lists
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Arguments And Messages    ${tc}

Run Keyword When Keyword And String Arguments After Empty Lists
    Check Test Case    ${TEST NAME}

Run Keyword If When Not Enough Arguments
    Check Test Case    ${TEST NAME}

Run Keyword When Run Keyword Does Not Take Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Arguments And Messages    ${tc}

Run Keyword If With List And Two Arguments That needs to Be Processed
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Arguments And Messages    ${tc}

Run Keyword If With List And One Argument That needs to Be Processed
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Arguments And Messages    ${tc}

*** Keywords ***
Check Keyword Arguments And Messages
    [Arguments]    ${tc}
    Check Keyword Data    ${tc.kws[0].kws[0]}    \\Log Many    args=\@{ARGS}
    Check Keyword Data    ${tc.kws[0].kws[0].kws[0]}    BuiltIn.Log Many    args=\@{args}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    c:\\temp\\foo
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[1]}    \${notvar}
