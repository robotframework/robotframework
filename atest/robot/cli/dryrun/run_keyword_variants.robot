*** Settings ***
Suite Setup       Run Tests    --dryrun --listener ${LISTENER}    cli/dryrun/run_keyword_variants.robot
Resource          atest_resource.robot

*** Variables ***
${LISTENER}       ${DATADIR}/cli/dryrun/LinenoListener.py

*** Test Cases ***
Run Keyword With Keyword with Invalid Number of Arguments
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc[0]}       BuiltIn.Run Keyword    args=Log    status=FAIL
    Check Keyword Data    ${tc[0, 0]}    BuiltIn.Log            args=       status=FAIL

Run Keyword With Missing Keyword
    Check Test Case    ${TESTNAME}

Keywords with variable in name are ignored
    Test Should Have Correct Keywords    kw_index=0
    Test Should Have Correct Keywords    BuiltIn.No Operation    kw_index=1
    Test Should Have Correct Keywords    kw_index=2
    Test Should Have Correct Keywords    BuiltIn.No Operation    kw_index=3

Keywords with variable in name are ignored also when variable is argument
    Check Test Case    ${TESTNAME}

Run Keyword With UK
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc[0]}          BuiltIn.Run Keyword If    args=True, UK    status=PASS
    Check Keyword Data    ${tc[0, 0]}       UK                                         status=PASS
    Check Keyword Data    ${tc[0, 0, 0]}    BuiltIn.No Operation                       status=NOT RUN

Run Keyword With Failing UK
    Check Test Case    ${TESTNAME}

Comment
    Check Test Case    ${TESTNAME}

Set Test/Suite/Global Variable
    Check Test Case    ${TESTNAME}

Variable Should (Not) Exist
    Check Test Case    ${TESTNAME}

Get Variable Value
    Check Test Case    ${TESTNAME}

Set Variable If
    Check Test Case    ${TESTNAME}

Run Keywords When All Keywords Pass
    Check Test Case    ${TESTNAME}

Run Keywords When One Keyword Fails
    Check Test Case    ${TESTNAME}

Run Keywords When Multiple Keyword Fails
    Check Test Case    ${TESTNAME}

Run Keywords With Arguments When All Keywords Pass
    Test Should Have Correct Keywords    BuiltIn.Log Many    BuiltIn.No Operation

Run Keywords With Arguments When One Keyword Fails
    Test Should Have Correct Keywords    BuiltIn.Log    BuiltIn.Log

Run Keywords With Arguments When Multiple Keyword Fails
    Test Should Have Correct Keywords    BuiltIn.Log    Unknown Keyword

Run Keywords With Arguments With Variables
    Test Should Have Correct Keywords    BuiltIn.Log

Run Keyword in For Loop Pass
    Check Test Case    ${TESTNAME}

Run Keyword in For Loop Fail
    Check Test Case    ${TESTNAME}

Wait Until Keyword Succeeds Pass
    Check Test Case    ${TESTNAME}

Wait Until Keyword Succeeds Fail
    Check Test Case    ${TESTNAME}

Run Keyword If Pass
    Check Test Case    ${TESTNAME}

Run Keyword If Fail
    Check Test Case    ${TESTNAME}

Run Keyword If with ELSE
    Check Test Case    ${TESTNAME}

Run Keyword If with ELSE IF
    Check Test Case    ${TESTNAME}

Run Keyword If with ELSE IF and ELSE
    Check Test Case    ${TESTNAME}

Run Keyword If with ELSE IF and ELSE without keywords
    Check Test Case    ${TESTNAME}

Run Keyword If with escaped or non-caps ELSE IF and ELSE
    Check Test Case    ${TESTNAME}

Run Keyword If with list variable in ELSE IF and ELSE
    Check Test Case    ${TESTNAME}

Test Teardown Related Run Keyword Variants
    Check Test Case    ${TESTNAME}

Given/When/Then
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc[0].body}    1
    Length Should Be    ${tc[1].body}    3
    Length Should Be    ${tc[2].body}    2
    Length Should Be    ${tc[3].body}    3
    Length Should Be    ${tc[4].body}    3

Line number
    Should Be Empty    ${ERRORS}
    ${tc} =    Check Test Case    Run Keyword With Missing Keyword
    Should Be Equal    ${tc[0].doc}       Keyword 'Run Keyword' on line 14.
    Should Be Equal    ${tc[0, 0].doc}    Keyword 'Missing' on line 14.
    ${tc} =    Check Test Case    Run Keywords When One Keyword Fails
    Should Be Equal    ${tc[0].doc}       Keyword 'Run Keywords' on line 68.
    Should Be Equal    ${tc[0, 0].doc}    Keyword 'Fail' on line 68.
    Should Be Equal    ${tc[0, 2].doc}    Keyword 'Log' on line 68.
    Should Be Equal    ${tc[0, 3].doc}    Keyword 'UK' on line 68.
    ${tc} =    Check Test Case    Run Keyword If Pass
    Should Be Equal    ${tc[0].doc}       Keyword 'Run Keyword If' on line 114.
    Should Be Equal    ${tc[0, 0].doc}    Keyword 'No Operation' on line 114.
