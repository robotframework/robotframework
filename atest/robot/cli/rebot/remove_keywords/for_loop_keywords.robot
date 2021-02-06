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
    ${tc}=    Check Test Case    Simple loop
    Length Should Be    ${tc.kws[1].kws}    1
    Should Be Equal     ${tc.kws[1].doc}    ${1 REMOVED}
    Should Be Equal     ${tc.kws[1].kws[0].status}    PASS

Failed Steps Are Not Removed
    ${tc}=    Check Test Case    Failure inside FOR 2
    Length Should Be    ${tc.kws[0].kws}                      1
    Should Be Equal     ${tc.kws[0].doc}                      ${3 REMOVED}
    Should Be Equal     ${tc.kws[0].kws[0].name}              \${num} = 4
    Should Be Equal     ${tc.kws[0].kws[0].status}            FAIL
    Length Should Be    ${tc.kws[0].kws[0].kws}               3
    Should Be Equal     ${tc.kws[0].kws[0].kws[-1].status}    NOT RUN

Steps With Warning Are Not Removed
    ${tc}=    Check Test Case    Variables in values
    Length Should Be     ${tc.kws[0].kws}    2
    Should Be Equal      ${tc.kws[0].doc}    ${4 REMOVED}
    Check Log Message    ${tc.kws[0].kws[0].kws[-1].kws[0].msgs[0]}    Presidential Candidate!    WARN
    Check Log Message    ${tc.kws[0].kws[1].kws[-1].kws[0].msgs[0]}    Presidential Candidate!    WARN

Steps From Nested Loops Are Removed
    ${tc}=    Check Test Case    Nested Loop Syntax
    Length Should Be    ${tc.kws[0].kws}    1
    Should Be Equal     ${tc.kws[0].doc}    ${2 REMOVED}
    Length Should Be    ${tc.kws[0].kws[0].kws[1].kws}    1
    Should Be Equal     ${tc.kws[0].kws[0].kws[1].doc}    ${2 REMOVED}

Steps From Loops In Keywords From Loops Are Removed
    ${tc}=    Check Test Case    Keyword with loop calling other keywords with loops
    Length Should Be    ${tc.kws[0].kws[0].kws}    1
    Should Be Equal     ${tc.kws[0].kws[0].doc}    ${0 REMOVED}
    Length Should Be    ${tc.kws[0].kws[0].kws[0].kws[0].kws[1].kws}    1
    Should Be Equal     ${tc.kws[0].kws[0].kws[0].kws[0].kws[1].doc}    ${1 REMOVED}
    Length Should Be    ${tc.kws[0].kws[0].kws[0].kws[1].kws[0].kws}    1
    Should Be Equal     ${tc.kws[0].kws[0].kws[0].kws[1].kws[0].doc}    ${1 REMOVED}

Empty Loops Are Handled Correctly
    ${tc}=    Check Test Case    Empty body
    Should Be Empty    ${tc.kws[0].kws}
    Should Be Equal    ${tc.kws[0].doc}    ${0 REMOVED}

*** Keywords ***
Remove For Loop Keywords With Rebot
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    running/for.robot
    Run Rebot    --removekeywords fOr    ${INPUTFILE}
