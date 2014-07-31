*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_with_errors.txt
Force Tags        regression
Default Tags      jybot    pybot
Resource          atest_resource.txt

*** Test Cases ***
Ignore Error When Keyword Passes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    My message

Ignore Error When Keyword Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    My error message    FAIL
    Should Be Equal    ${tc.kws[0].kws[0].status}    FAIL
    Should Be Equal    ${tc.kws[0].status}    PASS

Ignore Error Returns When Keyword Passes
    Check Test Case    ${TEST NAME}

Ignore Error Returns When Keyword Fails
    Check Test Case    ${TEST NAME}

Ignore Error With User Keyword When Keywords Pass
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    Hello world
    Should Be Equal    ${tc.kws[0].kws[0].kws[2].name}    \${ret} = BuiltIn.Evaluate

Ignore Error With User Keyword When Keyword Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].kws[0].msgs[0]}    Hello world
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    Expected failure in UK    FAIL
    Ints Equal    ${tc.kws[0].kws[0].keyword_count}    2

Ignore Error With Arguments That Needs To Be Escaped
    Check Test Case    ${TEST NAME}

Ignore Error When Timeout Occurs
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].status}    FAIL    Run Keyword And Ignore Error captured timeout even though it should not    no values

Ignore Error When Timeout Occurs In UK
    Check Test Case    ${TEST NAME}

Ignore Error When Syntax Error At Parsing Time
    Check Test Case    ${TEST NAME}

Ignore Error When Syntax Error At Run Time
    Check Test Case    ${TEST NAME}

Ignore Error When Syntax Error In Setting Variables
    Check Test Case    ${TEST NAME}

Ignore Error When Syntax Error In For Loop
    Check Test Case    ${TEST NAME}

Expect Error When Error Occurs
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    My error message    FAIL
    Should Be Equal    ${tc.kws[0].kws[0].status}    FAIL
    Should Be Equal    ${tc.kws[0].status}    PASS

Expect Error When Different Error Occurs
    Check Test Case    ${TEST NAME}
    Check Test Case    ${TEST NAME} 2

Expect Error When No Errors Occur
    Check Test Case    ${TEST NAME}

Expected Error Is Pattern
    Check Test Case    ${TEST NAME}

Expected Error Is Multiline
    Check Test Case    ${TEST NAME}

Expected Error Should Be Returned
    Check Test Case    ${TEST NAME}

Expect Error With User Keyword When Keywords Pass
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    Hello world
    Should Be Equal    ${tc.kws[0].kws[0].kws[2].name}    \${ret} = BuiltIn.Evaluate

Expect Error With User Keyword When Keyword Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].kws[0].msgs[0]}    Hello world
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    Expected failure in UK    FAIL
    Ints Equal    ${tc.kws[0].kws[0].keyword_count}    2

Expect Error With Arguments That Needs To Be Escaped
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    c:\\temp\\foo\\not_new_line
    Check Log Message    ${tc.kws[1].kws[0].msgs[1]}    \${notvar}

Expect Error When Timeout Occurs
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].status}    FAIL    Run Keyword And Expect Error captured timeout even though it should not    no values

Expect Error When Timeout Occurs In UK
    Check Test Case    ${TEST NAME}

Expect Error When Syntax Error At Parsing Time
    Check Test Case    ${TEST NAME}

Expect Error When Syntax Error At Run Time
    Check Test Case    ${TEST NAME}

Expect Error When Syntax Error In Setting Variables
    Check Test Case    ${TEST NAME}

Expect Error When Syntax Error In For Loop
    Check Test Case    ${TEST NAME}

Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    Ignore Error With Arguments That Needs To be Escaped
    Check KW Arguments    ${tc.kws[3].kws[0]}    \@{NEEDS ESCAPING}

