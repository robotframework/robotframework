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

Tidying many files in place
    Copy File    ${DATA}/golden_pipes.robot    ${TEMP}/
    Copy File    ${DATA}/golden.robot    ${TEMP}/
    Run tidy    --InPlace   ${TEMP}/golden*
    Check File Counts    robot=2
