*** Settings ***
Test Template     Run And Check Include And Exclude
Resource          atest_resource.robot

*** Variables ***
${DATA SOURCE}    tags/include_and_exclude.robot
${F}              force
${I1}             incl1
${I2}             incl 2
${I3}             incl_3
${E1}             excl1
${E2}             excl 2
${E3}             excl_3
@{INCL}           ${I1}    ${I2}    ${I3}
@{EXCL}           ${E1}    ${E2}    ${E3}
@{ALL}            @{EXCL}    ${F}    @{INCL}
@{INTERNAL}       robot:just-an-example    ROBOT : XXX

*** Test Cases ***
No Includes Or Excludes
    ${EMPTY}    @{ALL}

One Include
    --tagstatinclude incl1    ${I1}

Matching And Non Matching Includes
    --TagStatInclude INCL3 --TagStatInclude nonexisting    ${I3}

More Includes
    --TagStatI incl2 --TagStatI "incl 3" --TagStatI _ --TagStatI incl2    ${I2}    ${I3}

Include With Patterns
    --TagStatInc incl_?    @{INCL}
    --TagStatInc *cl3 --TagStatInc i*2    ${E3}    ${I2}    ${I3}

Include to show internal tags
    --tagstatinclude incl1 --tagstatinclude ROBOT:*    ${I1}    @{INTERNAL}
    --tagstatinclude robot:*    @{INTERNAL}
    --tagstatinclude=*    @{ALL}    @{INTERNAL}

Include and exclude internal
    --tagstatinclude incl1 --tagstatinclude "robot : *" --tagstatexclude ROBOT:*    ${I1}

One Exclude
    --tagstatexclude excl1    ${E2}    ${E3}    ${F}    @{INCL}

Matching And Non Matching Excludes
    --TagStatE EXCL3 --TagStatE nonexisting    ${E1}    ${E2}    ${F}    @{INCL}

More Excludes
    --TagStatExclude excl3 --TagStatExclude excl2    ${E1}    ${F}    @{INCL}

Exclude With Patterns
    --TagStatExc exc??    ${F}    @{INCL}
    --TagStatExc *3 --TagStatE e*2 --TagStatE e*1    ${F}    ${I1}    ${I2}

Include And Exclude
    --TagStatInc *_2 --TagStatExc EXCL_*    ${I2}

Non Matching Include
    --TagStatInclude nonex

Non Matching Exclude
    --TagStatExc nonexisting --TagStatExc nonex2    @{ALL}

Non Matching Include And Exclude
    --TagStatInc nonex --TagStatExc nonex2

*** Keywords ***
Run And Check Include And Exclude
    [Arguments]    ${params}    @{tags}
    Run Tests    ${params}    ${DATA SOURCE}
    Stderr Should Be Empty
    Tag Statistics Should Be    @{tags}

Tag Statistics Should Be
    [Arguments]    @{tags}
    ${stats} =    Get Tag Stat Nodes
    Should Be Equal    ${{ len($stats) }}    ${{ len($tags) }}
    FOR    ${stat}    ${tag}    IN ZIP    ${stats}    ${tags}
        Should Be Equal    ${stat.text}    ${tag}
    END
