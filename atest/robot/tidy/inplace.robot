*** Settings ***
Resource          tidy_resource.robot
Test Setup        Create Directory     ${TEMP}
Test Teardown     Remove Directory     ${TEMP}    recursive=True

*** Test Cases ***

Tidying single file in place
    [Setup]    Copy File    ${DATA}/golden.robot    ${TEMP}/golden.robot
    Run tidy    --inplace --usepipes    ${TEMP}/golden.robot
    Compare tidy results    ${TEMP}/golden.robot    ${DATA}/golden_pipes.robot
    Check File Counts    robot=1

Tidying single file in place and change format
    [Setup]    Copy File    ${DATA}/golden.robot    ${TEMP}/golden.robot
    Run tidy    -i -f html    ${TEMP}/golden.robot
    Compare tidy results    ${TEMP}/golden.html    ${DATA}/golden.html
    Check File Counts    html=1

Tidying many files in place
    Copy File    ${DATA}/golden_pipes.robot    ${TEMP}/
    Copy File    ${DATA}/golden.tsv    ${TEMP}/
    Run tidy    --InPlace --ForMat HtmL   ${TEMP}/golden*
    Check File Counts    html=2
