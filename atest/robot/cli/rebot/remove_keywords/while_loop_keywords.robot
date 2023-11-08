*** Settings ***
Suite Setup       Remove WHILE Keywords With Rebot
Suite Teardown    Remove File    ${INPUTFILE}
Resource          remove_keywords_resource.robot

*** Variables ***
${2 REMOVED}      <span class="robot-note">2 passing items removed using the --remove-keywords option.</span>
${4 REMOVED}      <span class="robot-note">4 passing items removed using the --remove-keywords option.</span>

*** Test Cases ***
Passed Steps Are Removed Except The Last One
    ${tc}=    Check Test Case    Loop executed multiple times
    Length Should Be    ${tc.kws[0].kws}                      1
    Should Be Equal     ${tc.kws[0].message}                  *HTML* ${4 REMOVED}
    Should Be Equal     ${tc.kws[0].kws[0].status}            PASS

Failed Steps Are Not Removed
    ${tc}=    Check Test Case     Execution fails after some loops
    Length Should Be    ${tc.kws[0].kws}                      1
    Should Be Equal     ${tc.kws[0].message}                  *HTML* Oh no, got 4<hr>${2 REMOVED}
    Should Be Equal     ${tc.kws[0].kws[0].status}            FAIL
    Length Should Be    ${tc.kws[0].kws[0].kws}               3
    Should Be Equal     ${tc.kws[0].kws[0].kws[-1].status}    NOT RUN

Steps From Nested Loops Are Removed
    ${tc}=    Check Test Case    Loop in loop
    Length Should Be    ${tc.kws[0].kws}                      1
    Should Be Equal     ${tc.kws[0].message}                  *HTML* ${4 REMOVED}
    Length Should Be    ${tc.kws[0].kws[0].kws[2].kws}        1
    Should Be Equal     ${tc.kws[0].kws[0].kws[2].message}    *HTML* ${2 REMOVED}

*** Keywords ***
Remove WHILE Keywords With Rebot
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    running/while/while.robot
    Run Rebot    --removekeywords while    ${INPUTFILE}
