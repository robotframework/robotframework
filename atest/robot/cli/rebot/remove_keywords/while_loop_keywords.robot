*** Settings ***
Suite Setup       Remove For Loop Keywords With Rebot
Suite Teardown    Remove File    ${INPUTFILE}
Resource          remove_keywords_resource.robot

*** Variables ***
${0 REMOVED}      ${EMPTY}
${1 REMOVED}      _1 passing step removed using --RemoveKeywords option._
${2 REMOVED}      _2 passing steps removed using --RemoveKeywords option._
${3 REMOVED}      _3 passing steps removed using --RemoveKeywords option._
${4 REMOVED}      _4 passing steps removed using --RemoveKeywords option._

*** Test Cases ***
Passed Steps Are Removed Except The Last One
    ${tc}=    Check Test Case    Loop executed multiple times
    Length Should Be    ${tc.kws[0].kws}    1
    Should Be Equal     ${tc.kws[0].doc}    ${4 REMOVED}
    Should Be Equal     ${tc.kws[0].kws[0].status}    PASS

Failed Steps Are Not Removed
    ${tc}=    Check Test Case     Execution fails after some loops
    Length Should Be    ${tc.kws[0].kws}                      1
    Should Be Equal     ${tc.kws[0].doc}                      ${2 REMOVED}
    Should Be Equal     ${tc.kws[0].kws[0].status}            FAIL
    Length Should Be    ${tc.kws[0].kws[0].kws}               3
    Should Be Equal     ${tc.kws[0].kws[0].kws[-1].status}    NOT RUN

Steps From Nested Loops Are Removed
    ${tc}=    Check Test Case    Loop in loop
    Length Should Be    ${tc.kws[0].kws}    1
    Should Be Equal     ${tc.kws[0].doc}    ${4 REMOVED}
    Length Should Be    ${tc.kws[0].kws[0].kws[2].kws}    1
    Should Be Equal     ${tc.kws[0].kws[0].kws[2].doc}    ${2 REMOVED}


*** Keywords ***
Remove For Loop Keywords With Rebot
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    running/while/while.robot
    Run Rebot    --removekeywords while    ${INPUTFILE}
