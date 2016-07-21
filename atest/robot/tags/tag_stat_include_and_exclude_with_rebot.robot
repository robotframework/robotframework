*** Settings ***
Suite Setup     Create Output With Robot  ${INPUT FILE}  ${EMPTY}  ${DATA SOURCE}
Suite Teardown  Remove File  ${INPUT FILE}
Resource        rebot_resource.robot
Test Template   Run And Check Include And Exclude

*** Variables ***
${DATA SOURCE}  tags/include_and_exclude.robot
${INPUT FILE}   %{TEMPDIR}${/}robot-test-tagstat.xml
${ESCAPES}      -E star:STAR -E quest:QUEST -E space:SP
${F}            force
${I1}           incl1
${I2}           incl 2
${I3}           incl_3
${E1}           excl1
${E2}           excl 2
${E3}           excl_3
@{INCL}         ${I1}    ${I2}    ${I3}
@{EXCL}         ${E1}    ${E2}    ${E3}
@{ALL}          @{EXCL}    ${F}    @{INCL}

*** Test Cases ***
No Includes Or Excludes
    ${EMPTY}    @{ALL}

One Include
    --tagstatinclude incl1    ${I1}

Matching And Non Matching Includes
    --TagStatInclude INCL3 --TagStatInclude nonexisting    ${I3}

More Includes
    --TagStatI incl2 --TagStatI inclSP3 --TagStatI _ --TagStatI incl2    ${I2}    ${I3}

Include With Patterns
    --TagStatInc incl_?    @{INCL}
    --TagStatInc STARcl3 --TagStatInc iSTAR2    ${E3}    ${I2}    ${I3}

One Exclude
    --tagstatexclude excl1    ${E2}    ${E3}    ${F}    @{INCL}

Matching And Non Matching Excludes
    --TagStatE EXCL3 --TagStatE nonexisting    ${E1}    ${E2}    ${F}   @{INCL}

More Excludes
    --TagStatExclude excl3 --TagStatExclude excl2    ${E1}    ${F}   @{INCL}

Exclude With Patterns
    --TagStatExc exc??    ${F}   @{INCL}
    --TagStatExc STAR3 --TagStatE eSTAR2 --TagStatE eSTAR1    ${F}    ${I1}    ${I2}

Include And Exclude
    --TagStatInc STAR_2 --TagStatExc EXCL_STAR    ${I2}

Non Matching Include
    --TagStatInclude nonex

Non Matching Exclude
    --TagStatExc nonexisting --TagStatExc nonex2    @{ALL}

Non Matching Include And Exclude
    --TagStatInc nonex --TagStatExc nonex2

*** Keywords ***

Run And Check Include And Exclude
    [Arguments]    ${params}    @{tags}
    Run Rebot    ${params} ${ESCAPES}    ${INPUT FILE}
    Stderr Should Be Empty
    Tag Statistics Should Be    @{tags}

Tag Statistics Should Be
    [Arguments]    @{tags}
    ${stats} =    Get Tag Stat Nodes
    Should Be Equal    ${stats.__len__()}    ${tags.__len__()}
    :: FOR    ${i}    IN RANGE    ${tags.__len__()}
    \    Should Be Equal    ${stats[${i}].text}    ${tags[${i}]}
