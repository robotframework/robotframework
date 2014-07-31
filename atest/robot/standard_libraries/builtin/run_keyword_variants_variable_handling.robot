*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_variants_variable_handling.txt
Force Tags        regression    jybot    pybot
Resource          atest_resource.txt

*** Variable ***
@{EXPECTED ARGS}    c:\\\\temp\\\\foo    \\\${notvar}

*** Test Case ***
Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check KW Arguments    ${tc.kws[0]}    My UK    Log    \${OBJECT}
    Check KW Arguments    ${tc.kws[0].kws[0]}    Log    \${OBJECT}
    Check KW Arguments    ${tc.kws[0].kws[0].kws[0]}    \${name}    \@{args}
    Check KW Arguments    ${tc.kws[0].kws[0].kws[0].kws[0]}    \@{args}

Run Keyword When Keyword and Arguments Are in List Variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check KW Arguments    ${tc.kws[0].kws[0]}    @{EXPECTED ARGS}
    Check KW Arguments    ${tc.kws[1].kws[0]}    \\\${notvar}

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

*** Keyword ***
Check Keyword Arguments And Messages
    [Arguments]    ${tc}
    Check KW Arguments    ${tc.kws[0].kws[0]}    \@{ARGS}
    Check KW Arguments    ${tc.kws[0].kws[0].kws[0]}    \@{args}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    c:\\temp\\foo
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[1]}    \${notvar}
