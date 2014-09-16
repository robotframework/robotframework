*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword.robot
Force Tags        regression      jybot    pybot
Resource          atest_resource.robot

*** Test Cases ***
Run Keyword
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword    ${tc.kws[0]}    BuiltIn.Log    This is logged with Run Keyword
    Should Be Equal    ${tc.kws[1].kws[0].name}    BuiltIn.No Operation
    Check Run Keyword    ${tc.kws[2]}    BuiltIn.Log Many    1    2    3    4    5
    Check Run Keyword    ${tc.kws[4]}    BuiltIn.Log    Run keyword with variable: Log
    Check Run Keyword    ${tc.kws[6]}    BuiltIn.Log Many    one    two

Run Keyword Returning Value
    ${tc} =    Check test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${ret} = BuiltIn.Run Keyword
    Should Be Equal    ${tc.kws[0].kws[0].name}    BuiltIn.Set Variable
    Should Be Equal    ${tc.kws[2].name}    \${ret} = BuiltIn.Run Keyword
    Should Be Equal    ${tc.kws[2].kws[0].name}    BuiltIn.Evaluate

Run Keyword With Arguments That Needs To Be Escaped
    ${tc} =    Check test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    c:\\temp\\foo
    Check Log Message    ${tc.kws[1].kws[0].msgs[1]}    \${notvar}

Escaping Arguments From Opened List Variable
    ${tc} =    Check test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    message=foo
    Check Log Message    ${tc.kws[3].kws[0].msgs[0]}    42

Run Keyword With UK
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword In UK    ${tc.kws[0]}    BuiltIn.Log    Using UK
    Check Run Keyword In UK    ${tc.kws[1]}    BuiltIn.Log Many    yksi    kaksi

Run Keyword In Multiple Levels And With UK
    Check test Case    ${TEST NAME}

Run Keyword In For Loop
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword    ${tc.kws[0].kws[0].kws[0]}    BuiltIn.Log    hello from for loop
    Check Run Keyword In UK    ${tc.kws[0].kws[2].kws[0]}    BuiltIn.Log    hei maailma
    Check Run Keyword    ${tc.kws[1].kws[0].kws[0]}    BuiltIn.Log    hello from second for loop

Run Keyword With Test Timeout
    Check Test Case    ${TEST NAME} Passing
    ${tc} =    Check Test Case    ${TEST NAME} Exceeded
    Check Run Keyword    ${tc.kws[0]}    BuiltIn.Log    Before Timeout

Run Keyword With KW Timeout
    Check test Case    ${TEST NAME} Passing
    Check test Case    ${TEST NAME} Exceeded

Run Keyword With Invalid Keyword Name
    Check Test Case    ${TEST NAME}

*** Keywords ***
Check Run Keyword
    [Arguments]    ${kw}    ${subkw_name}    @{msgs}
    Should Be Equal    ${kw.name}    BuiltIn.Run Keyword
    Should Be Equal    ${kw.kws[0].name}    ${subkw_name}
    ${index} =    Set Variable    ${0}
    :FOR    ${msg}    IN    @{msgs}
    \    Check Log Message    ${kw.kws[0].msgs[${index}]}    ${msg}
    \    ${index} =    evaluate    ${index} +1

Check Run Keyword In Uk
    [Arguments]    ${kw}    ${subkw_name}    @{msgs}
    Should Be Equal    ${kw.name}    BuiltIn.Run Keyword
    Should Be Equal    ${kw.kws[0].name}    My UK
    Check Run Keyword    ${kw.kws[0].kws[0]}    ${subkw_name}    @{msgs}

