*** Settings ***
Suite Setup     Run Tests  --dryrun  cli/dryrun/run_keyword_variants.robot
Resource        atest_resource.robot

*** Test Cases ***
Run Keyword With Keyword with Invalid Number of Arguments
    Check Test Case  ${TESTNAME}

Run Keyword With Missing Keyword
    Check Test Case  ${TESTNAME}

Keywords with variable in name are ignored
    Test Should Have Correct Keywords  kw_index=0
    Test Should Have Correct Keywords  BuiltIn.No Operation  kw_index=1
    Test Should Have Correct Keywords  kw_index=2
    Test Should Have Correct Keywords  BuiltIn.No Operation  kw_index=3

Keywords with variable in name are ignored also when variable is argument
    Check Test Case  ${TESTNAME}

Run Keyword With UK
    Check Test Case  ${TESTNAME}

Run Keyword With Failing UK
    Check Test Case  ${TESTNAME}

Comment
    Check Test Case  ${TESTNAME}

Set Test/Suite/Global Variable
    Check Test Case  ${TESTNAME}

Variable Should (Not) Exist
    Check Test Case  ${TESTNAME}

Get Variable Value
    Check Test Case  ${TESTNAME}

Set Variable If
    Check Test Case  ${TESTNAME}

Run Keywords When All Keywords Pass
    Check Test Case  ${TESTNAME}

Run Keywords When One Keyword Fails
    Check Test Case  ${TESTNAME}

Run Keywords When Multiple Keyword Fails
    Check Test Case  ${TESTNAME}

Run Keywords With Arguments When All Keywords Pass
    Test Should Have Correct Keywords  BuiltIn.Log Many  BuiltIn.No Operation

Run Keywords With Arguments When One Keyword Fails
    Test Should Have Correct Keywords  BuiltIn.Log  BuiltIn.Log

Run Keywords With Arguments When Multiple Keyword Fails
    Test Should Have Correct Keywords  BuiltIn.Log  Unknown Keyword

Run Keywords With Arguments With Variables
    Test Should Have Correct Keywords  BuiltIn.Log

Run Keyword in For Loop Pass
    Check Test Case  ${TESTNAME}

Run Keyword in For Loop Fail
    Check Test Case  ${TESTNAME}

Wait Until Keyword Succeeds Pass
    Check Test Case  ${TESTNAME}

Wait Until Keyword Succeeds Fail
    Check Test Case  ${TESTNAME}

Run Keyword If Pass
    Check Test Case  ${TESTNAME}

Run Keyword If Fail
    Check Test Case  ${TESTNAME}

Run Keyword If with ELSE
    Check Test Case  ${TESTNAME}

Run Keyword If with ELSE IF
    Check Test Case  ${TESTNAME}

Run Keyword If with ELSE IF and ELSE
    Check Test Case  ${TESTNAME}

Run Keyword If with ELSE IF and ELSE without keywords
    Check Test Case  ${TESTNAME}

Run Keyword If with escaped or non-caps ELSE IF and ELSE
    Check Test Case  ${TESTNAME}

Run Keyword If with list variable in ELSE IF and ELSE
    Check Test Case  ${TESTNAME}

Test Teardown Related Run Keyword Variants
    Check Test Case  ${TESTNAME}

Given/When/Then
    ${tc} =    Check Test Case  ${TESTNAME}
    Length Should Be    ${tc.kws[0].kws}    1
    Length Should Be    ${tc.kws[1].kws}    3
    Length Should Be    ${tc.kws[2].kws}    2
    Length Should Be    ${tc.kws[3].kws}    3
    Length Should Be    ${tc.kws[4].kws}    3
