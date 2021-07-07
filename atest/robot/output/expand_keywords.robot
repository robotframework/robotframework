*** Settings ***
Suite Setup        Run tests with expanding
Suite Teardown     No extra keyword should have been expanded
Test Template      Keyword should have been expanded
Library            LogDataFinder.py
Resource           atest_resource.robot

*** Variables ***
@{EXPANDED}        Set by Suite Setup
@{VALIDATED}

*** Test Cases ***
Keyword name
    s1-s1-k1    s1-s1-t1-k1    s1-s1-t2-k1        # name:MyKeyword

Keyword name with library prefix
    s1-s2-t1-k3    s1-s4-t2-k2-k1                 # NAME:BuiltIn.Sleep

Non-ASCII name
    s1-s2-t8-k1                                   # Name:Ñöñ-ÄŚÇÏÏ Këywörd Nämë

Name with special characters
    s1-s3-t2-k1                                   # name:<blink>NO</blink>

Name as pattern
    s1-s2-t1-k1    s1-s2-t3-k1                    # name:nonasciilib????.PRINT*

Keyword tag
    s1-s4-t1-k3                                   # tag:tags

Tag as pattern
    s1-s4-t2-k3-k1    s1-s4-t2-k4                 # TAG:Nest*2

*** Keywords ***
Run tests with expanding
    ${options} =    Catenate
    ...    --log log.html
    ...    --expandkeywords name:MyKeyword
    ...    --ExpandKeywords NAME:BuiltIn.Sleep
    ...    --expand "Name:???-Ä* K?ywörd Näm?"
    ...    --expandkeywords name:<blink>NO</blink>
    ...    --expandkeywords name:nonasciilib????.Print*
    ...    --expandkeywords name:NoMatch
    ...    --expandkeywords tag:tags
    ...    --ExpandKeywords TAG:Nest*2
    ...    --expandkeywords tag:NoMatch
    ${paths} =    Catenate
    ...    misc/pass_and_fail.robot
    ...    misc/non_ascii.robot
    ...    misc/formatting_and_escaping.robot
    ...    misc/normal.robot
    ...    misc/if_else.robot
    ...    misc/for_loops.robot
    Run Tests    ${options}    ${paths}
    ${EXPANDED} =    Get Expand Keywords    ${OUTDIR}/log.html
    Set Suite Variable    ${EXPANDED}

Keyword should have been expanded
    [Arguments]    @{ids}
    List Should Contain Sub List    ${EXPANDED}    ${ids}
    Append To List    ${VALIDATED}    @{ids}

No extra keyword should have been expanded
    Sort List    ${EXPANDED}
    Sort List    ${VALIDATED}
    Log List    ${EXPANDED}
    Log list    ${VALIDATED}
    Lists Should Be Equal    ${EXPANDED}    ${VALIDATED}
