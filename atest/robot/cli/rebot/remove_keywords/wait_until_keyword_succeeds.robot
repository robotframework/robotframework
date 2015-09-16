*** Settings ***
Suite Setup       Remove Wait Until Keyword Succeeds with Rebot
Resource          remove_keywords_resource.robot

*** Variables ***
${DOC}            Runs the specified keyword and retries if it fails.

*** Test Cases ***
Last failing Step is not removed
    ${tc}=    Check Number Of Keywords     Fail Until The End    1
    Should Match    ${tc.kws[0].doc}    ${DOC}\n\n_? failing step* removed using --RemoveKeywords option._

Last passing Step is not removed
    ${tc}=    Check Number Of Keywords    Passes before timeout    2
    Should Be Equal    ${tc.kws[0].doc}    ${DOC}\n\n_1 failing step removed using --RemoveKeywords option._

Steps containing warnings are not removed
    ${tc}=   Check Number Of Keywords    Warnings    3
    Should be Equal    ${tc.kws[0].doc}    ${DOC}
    Check Number Of Keywords    One Warning    2

Nested Wait Until keywords are removed
    ${tc}=    Check Test Case    Nested
    Length Should Be    ${tc.kws[0].kws}    1
    Length Should Be    ${tc.kws[0].kws[0].kws}    1

*** Keywords ***
Remove Wait Until Keyword Succeeds with Rebot
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    cli/remove_keywords/wait_until_keyword_succeeds.robot
    Run Rebot    --removekeywords wuKs    ${INPUTFILE}

Check Number Of Keywords
    [Arguments]    ${test name}    ${expected number}
    ${tc}=    Check Test Case    ${test name}
    Length Should Be    ${tc.kws[0].kws}    ${expected number}
    [Return]    ${tc}

