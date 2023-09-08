*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${ORIG_START}     Set in Create Output With Robot
${ORIG_END}       -- ;; --
${ORIG_ELAPSED}   -- ;; --

*** Keywords ***
Create Output With Robot
    [Arguments]    ${outputname}    ${options}    ${sources}
    Run Tests    ${options}    ${sources}
    Timestamp Should Be Valid       ${SUITE.start_time}
    Timestamp Should Be Valid       ${SUITE.end_time}
    Elapsed Time Should Be Valid    ${SUITE.elapsed_time}
    Set Suite Variable    $ORIG_START      ${SUITE.start_time}
    Set Suite Variable    $ORIG_END        ${SUITE.end_time}
    Set Suite Variable    $ORIG_ELAPSED    ${SUITE.elapsed_time}
    IF    $outputname    Move File    ${OUTFILE}    ${outputname}
