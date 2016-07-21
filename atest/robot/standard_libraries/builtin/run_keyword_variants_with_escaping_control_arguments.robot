*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_variants_with_escaping_control_arguments.robot
Resource          atest_resource.robot

*** Test Cases ***
Run Keyword with Run Keywords with Arguments Inside List variable should escape AND
    ${tc}=    Test Should Have Correct Keywords    BuiltIn.Run Keywords
    Check Log Message    ${tc.kws[0].kws[0].kws[0].kws[0].msgs[0]}    log message

Run Keyword with Run Keywords and Arguments Inside List variable should escape AND
    ${tc}=    Test Should Have Correct Keywords    BuiltIn.Run Keywords
    Check Log Message    ${tc.kws[0].kws[0].kws[0].kws[0].msgs[0]}    log message

Run Keyword If with Run Keywords With Arguments Inside List variable should escape AND
    ${tc}=    Test Should Have Correct Keywords    BuiltIn.Run Keywords
    Check Log Message    ${tc.kws[0].kws[0].kws[0].kws[0].msgs[0]}    log message

Run Keyword If with Run Keywords And Arguments Inside List variable should escape AND
    ${tc}=    Test Should Have Correct Keywords    BuiltIn.Run Keyword
    Check Log Message    ${tc.kws[0].kws[0].kws[0].kws[0].kws[0].msgs[0]}    log message

Run Keywords With Run Keyword If should not escape ELSE and ELSE IF
    ${tc}=    Test Should Have Correct Keywords
    ...    BuiltIn.Run Keyword If    BuiltIn.Log    BuiltIn.Run Keyword If
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    log message
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    that

Run Keywords With Run Keyword If In List Variable Should Escape ELSE and ELSE IF From List Variable
    ${tc}=    Test Should Have Correct Keywords
    ...    BuiltIn.Run Keyword If    BuiltIn.Log    BuiltIn.Run Keyword If
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    that

Run Keywords With Run Keyword If With Arguments From List Variable should escape ELSE and ELSE IF From List Variable
    ${tc}=    Test Should Have Correct Keywords
    ...    BuiltIn.Run Keyword If    BuiltIn.Log    BuiltIn.Run Keyword If
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    that
