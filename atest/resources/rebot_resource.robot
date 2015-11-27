*** Setting ***
Resource          atest_resource.robot

*** Variable ***
${ORIG_START}     Set in Create Output With Robot
${ORIG_END}       -- ;; --
${ORIG_ELAPSED}   -- ;; --

*** Keyword ***
Create Output With Robot
    [Arguments]    ${outputname}    ${options}    ${sources}
    Run Tests    ${options}    ${sources}
    Timestamp Should Be Valid    ${SUITE.starttime}
    Timestamp Should Be Valid    ${SUITE.endtime}
    Elapsed Time Should Be Valid    ${SUITE.elapsedtime}
    Set Suite Variable    $ORIG_START    ${SUITE.starttime}
    Set Suite Variable    $ORIG_END    ${SUITE.endtime}
    Set Suite Variable    $ORIG_ELAPSED    ${SUITE.elapsedtime}
    Run Keyword If    $outputname    Move File    ${OUTFILE}    ${outputname}

Check times
    [Arguments]    ${item}    ${start}    ${end}    ${elapsed}
    Should Be Equal    ${item.starttime}    ${start}
    Should Be Equal    ${item.endtime}    ${end}
    Should Be Equal As Integers    ${item.elapsedtime}    ${elapsed}
