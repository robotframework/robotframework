*** Settings ***
Suite Setup       Remove For Loop Keywords With Rebot
Suite Teardown    Remove File    ${INPUTFILE}
Resource          remove_keywords_resource.robot

*** Variables ***
${1 REMOVED}      <i>1 passing step removed using --RemoveKeywords option.</i>
${2 REMOVED}      <i>2 passing steps removed using --RemoveKeywords option.</i>
${3 REMOVED}      <i>3 passing steps removed using --RemoveKeywords option.</i>
${4 REMOVED}      <i>4 passing steps removed using --RemoveKeywords option.</i>

*** Test Cases ***
Passed Steps Are Removed Except The Last One
    ${tc}=    Check Test Case    Simple loop
    Length Should Be    ${tc.kws[1].kws}              1
    Should Be Equal     ${tc.kws[1].message}          *HTML* ${1 REMOVED}
    Should Be Equal     ${tc.kws[1].kws[0].status}    PASS

Failed Steps Are Not Removed
    ${tc}=    Check Test Case    Failure inside FOR 2
    Length Should Be    ${tc.body[0].body}                         1
    Should Be Equal     ${tc.body[0].message}                      *HTML* Failure with &lt;4&gt;<hr>${3 REMOVED}
    Should Be Equal     ${tc.body[0].body[0].type}                 ITERATION
    Should Be Equal     ${tc.body[0].body[0].assign['\${num}']}    4
    Should Be Equal     ${tc.body[0].body[0].status}               FAIL
    Length Should Be    ${tc.body[0].body[0].body}                 3
    Should Be Equal     ${tc.body[0].body[0].body[-1].status}      NOT RUN

Steps With Warning Are Not Removed
    ${tc}=    Check Test Case    Variables in values
    Length Should Be     ${tc.kws[0].kws}                              2
    Should Be Equal      ${tc.kws[0].message}                          *HTML* ${4 REMOVED}
    Check Log Message    ${tc.kws[0].kws[0].kws[-1].kws[0].msgs[0]}    Presidential Candidate!    WARN
    Check Log Message    ${tc.kws[0].kws[1].kws[-1].kws[0].msgs[0]}    Presidential Candidate!    WARN

Steps From Nested Loops Are Removed
    ${tc}=    Check Test Case    Nested Loop Syntax
    Length Should Be    ${tc.kws[0].kws}                      1
    Should Be Equal     ${tc.kws[0].message}                  *HTML* ${2 REMOVED}
    Length Should Be    ${tc.kws[0].kws[0].kws[1].kws}        1
    Should Be Equal     ${tc.kws[0].kws[0].kws[1].message}    *HTML* ${2 REMOVED}

Steps From Loops In Keywords From Loops Are Removed
    ${tc}=    Check Test Case    Keyword with loop calling other keywords with loops
    Length Should Be    ${tc.kws[0].kws[0].kws}                             1
    Should Be Equal     ${tc.kws[0].kws[0].message}                         This ought to be enough
    Length Should Be    ${tc.kws[0].kws[0].kws[0].kws[0].kws[1].kws}        1
    Should Be Equal     ${tc.kws[0].kws[0].kws[0].kws[0].kws[1].message}    *HTML* ${1 REMOVED}
    Length Should Be    ${tc.kws[0].kws[0].kws[0].kws[1].kws[0].kws}        1
    Should Be Equal     ${tc.kws[0].kws[0].kws[0].kws[1].kws[0].message}    *HTML* ${1 REMOVED}

Empty Loops Are Handled Correctly
    ${tc}=    Check Test Case    Empty body
    Should Be Equal    ${tc.body[0].status}            FAIL
    Should Be Equal    ${tc.body[0].message}           FOR loop cannot be empty.
    Should Be Equal    ${tc.body[0].body[0].type}      ITERATION
    Should Be Equal    ${tc.body[0].body[0].status}    NOT RUN
    Should Be Empty    ${tc.body[0].body[0].body}

*** Keywords ***
Remove For Loop Keywords With Rebot
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    running/for/for.robot
    Run Rebot    --removekeywords fOr    ${INPUTFILE}
