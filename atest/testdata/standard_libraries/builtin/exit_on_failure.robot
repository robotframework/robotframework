*** Settings ***
Library         Exceptions

*** Test Cases ***
Wait Until Keyword Succeeds
    [Documentation]  FAIL  FatalCatastrophyException: BANG!
    Wait Until Keyword Succeeds  1 seconds  0.1 second  Exit On Failure

Run Keyword And Expect Error
    [Documentation]  FAIL  FatalCatastrophyException: BANG!
    Run Keyword And Expect Error  *  Exit On Failure

Run Keyword And Ignore Error
    [Documentation]  FAIL  FatalCatastrophyException: BANG!
    Run Keyword And Ignore Error  Exit On Failure

Failing Test Case
    [Documentation]  FAIL  Test execution stopped due to a fatal error.
    Fail  This test should failt to exit on failure

