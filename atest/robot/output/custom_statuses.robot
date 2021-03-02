*** Settings ***
Suite Setup       Run With Custom Statuses
Resource          atest_resource.robot

*** Variables ***
${ADDSTATUS}      --AddStatus WIP:PASS:wip:blue --addstatus KNOWN-ISSUE:FAIL:known-*:purple --ADDSTATUS NON-CRITICAL:SKIP:non-criticalNOTwip:pink --log log.html
${ERROR}          [ ERROR ] Invalid format for option '--addstatus'. Expected 'NEWSTATUS:OLDSTATUS:TAGPATTERN:COLOR' but got 'invalid'.${USAGE TIP}\n

*** Test Cases ***
Check statuses
    Should Be Equal    ${TC1.status}    WIP
    Log should have correct custom status color    WIP    blue
    Should Be Equal    ${TC2.status}    KNOWN-ISSUE
    Log should have correct custom status color    KNOWN-ISSUE    purple
    Should Be Equal    ${TC3.status}    NON-CRITICAL
    Log should have correct custom status color    NON-CRITICAL    pink

Invalid usage
    Run Tests Without Processing Output    --AddStatus invalid    output/custom_statuses.robot
    Stderr Should Be Equal To    ${ERROR}

*** Keywords ***
Run With Custom Statuses
    Run Tests    ${ADDSTATUS}    output/custom_statuses.robot
    ${LOG} =    Get File    ${OUTDIR}/log.html
    Set Suite Variable    $LOG
    ${TC1} =    Check Test Case    Pass    message=Pass
    Set Suite Variable    $TC1
    ${TC2} =    Check Test Case    Fail    message=Fail
    Set Suite Variable    $TC2
    ${TC3} =    Check Test Case    Skip    message=Skip
    Set Suite Variable    $TC3

Log should have correct custom status color
    [Arguments]    ${status}    ${color}
    Log    ${LOG}
    Should Contain    ${LOG}    "${status}":"${color}"
