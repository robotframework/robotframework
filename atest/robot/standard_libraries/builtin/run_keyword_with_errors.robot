*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_with_errors.robot
Resource          atest_resource.robot

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
    Check Keyword Data    ${tc.kws[0].kws[0].kws[2]}    BuiltIn.Evaluate    \${ret}   1+2

Ignore Error With User Keyword When Keyword Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].kws[0].msgs[0]}    Hello world
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    Expected failure in UK    FAIL
    Length Should Be     ${tc.kws[0].kws[0].kws}    3
    Should Be Equal      ${tc.kws[0].kws[0].kws[-1].status}    NOT RUN

Ignore Error With Arguments That Needs To Be Escaped
    Check Test Case    ${TEST NAME}

Ignore Error When Timeout Occurs
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].status}    FAIL    Run Keyword And Ignore Error captured timeout even though it should not    no values

Ignore Error When Timeout Occurs In UK
    Check Test Case    ${TEST NAME}

Ignore Error Cannot Catch Syntax Errors
    Check Test Case    ${TEST NAME}

Ignore Error Can Catch Non-Syntax Errors
    Check Test Case    ${TEST NAME}

Ignore Error When Syntax Error In Setting Variables
    Check Test Case    ${TEST NAME}

Ignore Error When Invalid Return Values When Setting Variables
    Check Test Case    ${TEST NAME}

Ignore Error When Syntax Error In For Loop
    Check Test Case    ${TEST NAME}

Ignore Error When Non Existing Variable In For Loop
    Check Test Case    ${TEST NAME}

Ignore Error When Access To Nonexisting Variable
    Check Test Case    ${TEST NAME}

Ignore Error When Access To List Variable Nonexisting Index Syntax
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Ignore Error When Access To Dictionary Nonexisting Key Syntax
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Ignore Error With "Passing" Exceptions
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
    Check Keyword Data    ${tc.kws[0].kws[0].kws[2]}    BuiltIn.Evaluate    \${ret}   1+2

Expect Error With User Keyword When Keyword Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].kws[0].msgs[0]}    Hello world
    Check Log Message    ${tc.kws[0].kws[0].kws[1].msgs[0]}    Expected failure in UK    FAIL
    Length Should Be     ${tc.kws[0].kws[0].kws}    3
    Should Be Equal      ${tc.kws[0].kws[0].kws[-1].status}    NOT RUN

Expect Error With Arguments That Needs To Be Escaped
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    c:\\temp\\foo\\not_new_line
    Check Log Message    ${tc.kws[1].kws[0].msgs[1]}    \${notvar}

Expect Error When Timeout Occurs
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].status}    FAIL    Run Keyword And Expect Error captured timeout even though it should not    no values

Expect Error When Timeout Occurs In UK
    Check Test Case    ${TEST NAME}

Expect Error Cannot Catch Syntax Errors
    Check Test Case    ${TEST NAME}

Expect Error Can Catch Non-Syntax Errors
    Check Test Case    ${TEST NAME}

Expect Error When Syntax Error In Setting Variables
    Check Test Case    ${TEST NAME}

Expect Error When Invalid Return Values When Setting Variables
    Check Test Case    ${TEST NAME}

Expect Error When Syntax Error In For Loop
    Check Test Case    ${TEST NAME}

Expect Error When Non Existing Variable In For Loop
    Check Test Case    ${TEST NAME}

Expect Error When Access To Nonexisting Variable
    Check Test Case    ${TEST NAME}

Expect Error When Access To List Variable Nonexisting Index Syntax
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Expect Error When Access To Dictionary Nonexisting Key Syntax
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Expect Error With Explicit GLOB
    Check Test Case    ${TEST NAME}

Expect Error With EQUALS
    Check Test Case    ${TEST NAME}

Expect Error With STARTS
    Check Test Case    ${TEST NAME}

Expect Error With REGEXP
    Check Test Case    ${TEST NAME}

Expect Error With REGEXP requires full match
    Check Test Case    ${TEST NAME}

Expect Error With Unrecognized Prefix
    Check Test Case    ${TEST NAME}

Expect Error With "Passing" Exceptions
    Check Test Case    ${TEST NAME}

Variable Values Should Not Be Visible As Keyword's Arguments
    ${tc} =    Check Test Case    Ignore Error With Arguments That Needs To be Escaped
    Check Keyword Data    ${tc.kws[3].kws[0]}    BuiltIn.Create List    args=\@{NEEDS ESCAPING}
