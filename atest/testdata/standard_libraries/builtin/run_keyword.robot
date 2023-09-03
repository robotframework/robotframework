*** Settings ***
Library              OperatingSystem
Library              embedded_args.py
Variables            variable.py

*** Variables ***
@{NEEDS ESCAPING}    c:\\temp\\foo    \${notvar}    ${42}
${FAIL KW}           Fail
${VARIABLE}          value

*** Test Cases ***
Run Keyword
    [Documentation]    FAIL Expected failure
    Run Keyword    BuiltIn.Log    This is logged with Run Keyword
    Run Keyword    No Operation
    Run Keyword    Log many    1    2    3    ${4}    5
    ${kw} =    Set Variable    Log
    Run Keyword    ${kw}    Run keyword with variable: ${kw}
    @{kw} =    Set Variable    Log Many    one    two
    Run Keyword    @{kw}
    Run Keyword    ${FAIL KW}    Expected failure

Run Keyword Returning Value
    ${ret} =    Run Keyword    Set Variable    hello world
    Should Be Equal    ${ret}    hello world
    ${ret} =    Run Keyword    Evaluate    1+2
    Should Be Equal    ${ret}    ${3}

Run Keyword With Arguments That Needs To Be Escaped
    Run Keyword    Directory Should Exist    ${CURDIR}
    Run Keyword    Log Many    @{NEEDS ESCAPING}    ${CURDIR}    ${EMPTY}
    ${ret} =    Run Keyword    Create List    @{NEEDS ESCAPING}
    Should Be Equal    ${ret}    ${NEEDS ESCAPING}

Escaping Arguments From Opened List Variable
    @{named} =    Create List    Log    message=foo    INFO
    Run Keyword    @{named}
    @{nonstr} =    Create List    Log    ${42}    INFO
    Run Keyword    @{nonstr}

Run Keyword With UK
    [Documentation]    FAIL Expected failure in UK
    Run Keyword    My UK    Log    Using UK
    Run Keyword    My UK    Log Many    yksi    kaksi
    @{args} =    Set Variable    My UK    Log    Using UK
    Run Keyword    @{args}
    Run Keyword    My UK    Fail    Expected failure in UK

Run Keyword In Multiple Levels And With UK
    [Documentation]    FAIL Expected Failure
    Run Keyword    Run Keyword    Run Keyword    My UK    Run Keyword
    ...    My UK    My UK    My UK    Run Keyword    Fail    Expected Failure

With keyword accepting embedded arguments
    Run Keyword    Embedded "arg"

With library keyword accepting embedded arguments
    Run Keyword    Embedded "arg" in library

With keyword accepting embedded arguments as variables
    Run Keyword    Embedded "${VARIABLE}"
    Run Keyword    Embedded "${1}"

With library keyword accepting embedded arguments as variables
    Run Keyword    Embedded "${VARIABLE}" in library
    Run Keyword    Embedded "${1}" in library

With keyword accepting embedded arguments as variables containing objects
    Run Keyword    Embedded "${OBJECT}"
    Run Keyword    Embedded object "${OBJECT}"

With library keyword accepting embedded arguments as variables containing objects
    Run Keyword    Embedded "${OBJECT}" in library
    Run Keyword    Embedded object "${OBJECT}" in library

Run Keyword In For Loop
    [Documentation]    FAIL Expected failure in For Loop
    FOR    ${kw}              ${arg1}                ${arg2}    IN
    ...    Log                hello from for loop    INFO
    ...    BuiltIn.Comment    hi                     you
    ...    My UK              Log                    hei maailma
        Run Keyword    ${kw}    ${arg1}    ${arg2}
    END
    FOR    ${kw}    ${arg}    IN
    ...    Log      hello from second for loop
    ...    Fail     Expected failure in For Loop
        Run Keyword    ${kw}    ${arg}
    END

Run Keyword With Test Timeout Passing
    [Timeout]    5 seconds
    Run Keyword    Log    Timeout is not exceeded

Run Keyword With Test Timeout Exceeded
    [Documentation]    FAIL Test timeout 1 second 234 milliseconds exceeded.
    [Timeout]    1234 milliseconds
    Run Keyword    Log    Before Timeout
    Run Keyword    Sleep    1.3s

Run Keyword With KW Timeout Passing
    Run Keyword    Timeoutted UK Passing

Run Keyword With KW Timeout Exceeded
    [Documentation]    FAIL Keyword timeout 300 milliseconds exceeded.
    Run Keyword    Timeoutted UK Timeouting

Run Keyword With Invalid Keyword Name
    [Documentation]    FAIL Keyword name must be a string.
    Run Keyword    ${42}    arg 1    arg 2

*** Keywords ***
My UK
    [Arguments]    ${name}    @{args}
    Run Keyword    ${name}    @{args}

Run Keyword If
    [Arguments]    ${name}    ${condition}    @{args}
    BuiltIn.Run Keyword If    ${name}    ${condition}    @{args}

Timeoutted UK Passing
    [Timeout]    5 seconds
    No Operation

Timeoutted UK Timeouting
    [Timeout]    300 milliseconds
    Sleep    1 second

Embedded "${arg}"
    Log    ${arg}

Embedded object "${obj}"
    Log    ${obj}
    Should Be Equal    ${obj.name}    Robot
