*** Settings ***
Suite Setup       Remove Wait Until Keyword Succeeds with Rebot
Resource          remove_keywords_resource.robot

*** Test Cases ***
Last failing Step is not removed
    ${tc}=    Check Number Of Keywords     Fail Until The End    1
    ${expected} =    Catenate
    ...    [*]HTML[*] Keyword 'Fail' failed after retrying for 50 milliseconds.
    ...    The last error was: Not gonna happen<hr><span class="robot-note">? failing item* removed using the --remove-keywords option.</span>
    Should Match    ${tc.body[0].message}    ${expected}

Last passing Step is not removed
    ${tc}=    Check Number Of Keywords    Passes before timeout    2
    Should Be Equal    ${tc.body[0].message}    *HTML* <span class="robot-note">1 failing item removed using the --remove-keywords option.</span>

Steps containing warnings are not removed
    ${tc}=   Check Number Of Keywords    Warnings    3
    Should be Equal    ${tc.body[0].message}    ${EMPTY}
    Check Number Of Keywords    One Warning    2

Nested Wait Until keywords are removed
    ${tc}=    Check Test Case    Nested
    Length Should Be    ${tc.body[0].body.filter(messages=False)}    1
    Length Should Be    ${tc.body[0].body[0].body}                   1

*** Keywords ***
Remove Wait Until Keyword Succeeds with Rebot
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    cli/remove_keywords/wait_until_keyword_succeeds.robot
    Run Rebot    --removekeywords wuKs    ${INPUTFILE}

Check Number Of Keywords
    [Arguments]    ${name}    ${expected}
    ${tc}=    Check Test Case    ${name}
    Length Should Be    ${tc.body[0].body.filter(messages=False)}    ${expected}
    RETURN    ${tc}

