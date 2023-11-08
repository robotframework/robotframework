*** Settings ***
Suite Setup       Run Tests    --listener ${CURDIR}${/}listener_printing_start_end_kw.py    standard_libraries/builtin/run_keyword.robot
Resource          atest_resource.robot

*** Test Cases ***
Run Keyword
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword     ${tc.kws[0]}           BuiltIn.Log    This is logged with Run Keyword
    Check Keyword Data    ${tc.kws[1].kws[0]}    BuiltIn.No Operation
    Check Run Keyword     ${tc.kws[2]}           BuiltIn.Log Many    1    2    3    4    5
    Check Run Keyword     ${tc.kws[4]}           BuiltIn.Log    Run keyword with variable: Log
    Check Run Keyword     ${tc.kws[6]}           BuiltIn.Log Many    one    two

Run Keyword Returning Value
    ${tc} =    Check test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}           BuiltIn.Run Keyword    \${ret}    Set Variable, hello world
    Check Keyword Data    ${tc.kws[0].kws[0]}    BuiltIn.Set Variable    args=hello world
    Check Keyword Data    ${tc.kws[2]}           BuiltIn.Run Keyword    \${ret}    Evaluate, 1+2
    Check Keyword Data    ${tc.kws[2].kws[0]}    BuiltIn.Evaluate    args=1+2

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

With keyword accepting embedded arguments
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword With Embedded Args    ${tc.kws[0]}    Embedded "arg"    arg

With library keyword accepting embedded arguments
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword With Embedded Args    ${tc.kws[0]}   Embedded "arg" in library    arg

With keyword accepting embedded arguments as variables
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword With Embedded Args    ${tc.kws[0]}    Embedded "\${VARIABLE}"    value
    Check Run Keyword With Embedded Args    ${tc.kws[1]}    Embedded "\${1}"           1

With library keyword accepting embedded arguments as variables
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword With Embedded Args    ${tc.kws[0]}    Embedded "\${VARIABLE}" in library    value
    Check Run Keyword With Embedded Args    ${tc.kws[1]}    Embedded "\${1}" in library           1

With keyword accepting embedded arguments as variables containing objects
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword With Embedded Args    ${tc.kws[0]}    Embedded "\${OBJECT}"           Robot
    Check Run Keyword With Embedded Args    ${tc.kws[1]}    Embedded object "\${OBJECT}"    Robot

With library keyword accepting embedded arguments as variables containing objects
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword With Embedded Args    ${tc.kws[0]}    Embedded "\${OBJECT}" in library          Robot
    Check Run Keyword With Embedded Args    ${tc.kws[1]}    Embedded object "\${OBJECT}" in library    Robot

Run Keyword In For Loop
    ${tc} =    Check test Case    ${TEST NAME}
    Check Run Keyword          ${tc.kws[0].kws[0].kws[0]}    BuiltIn.Log    hello from for loop
    Check Run Keyword In UK    ${tc.kws[0].kws[2].kws[0]}    BuiltIn.Log    hei maailma
    Check Run Keyword          ${tc.kws[1].kws[0].kws[0]}    BuiltIn.Log    hello from second for loop

Run Keyword With Test Timeout
    Check Test Case    ${TEST NAME} Passing
    ${tc} =    Check Test Case    ${TEST NAME} Exceeded
    Check Run Keyword    ${tc.kws[0]}    BuiltIn.Log    Before Timeout

Run Keyword With KW Timeout
    Check test Case    ${TEST NAME} Passing
    Check test Case    ${TEST NAME} Exceeded

Run Keyword With Invalid Keyword Name
    Check Test Case    ${TEST NAME}

Stdout and stderr are not captured when running Run Keyword
    ${expected} =    Catenate    SEPARATOR=\n
    ...    start keyword BuiltIn.Run Keyword
    ...    start keyword My UK
    ...    start keyword BuiltIn.Run Keyword
    ...    start keyword BuiltIn.Log
    ...    end keyword BuiltIn.Log
    ...    end keyword BuiltIn.Run Keyword
    ...    end keyword My UK
    ...    end keyword BuiltIn.Run Keyword
    Stdout Should Contain    ${expected}
    Stderr Should Contain    ${expected}

*** Keywords ***
Check Run Keyword
    [Arguments]    ${kw}    ${subkw_name}    @{msgs}
    Should Be Equal    ${kw.full_name}           BuiltIn.Run Keyword
    Should Be Equal    ${kw.kws[0].full_name}    ${subkw_name}
    FOR    ${index}    ${msg}    IN ENUMERATE   @{msgs}
        Check Log Message    ${kw.kws[0].msgs[${index}]}    ${msg}
    END

Check Run Keyword In Uk
    [Arguments]    ${kw}    ${subkw_name}    @{msgs}
    Should Be Equal      ${kw.full_name}           BuiltIn.Run Keyword
    Should Be Equal      ${kw.kws[0].full_name}    My UK
    Check Run Keyword    ${kw.kws[0].kws[0]}       ${subkw_name}    @{msgs}

Check Run Keyword With Embedded Args
    [Arguments]    ${kw}    ${subkw_name}    ${msg}
    Should Be Equal    ${kw.full_name}    BuiltIn.Run Keyword
    IF    ${subkw_name.endswith('library')}
        Should Be Equal      ${kw.kws[0].full_name}       embedded_args.${subkw_name}
        Check Log Message    ${kw.kws[0].msgs[0]}         ${msg}
    ELSE
        Should Be Equal      ${kw.kws[0].full_name}              ${subkw_name}
        Should Be Equal      ${kw.kws[0].kws[0].full_name}       BuiltIn.Log
        Check Log Message    ${kw.kws[0].kws[0].msgs[0]}         ${msg}
    END
