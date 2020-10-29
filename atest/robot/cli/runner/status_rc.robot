*** Settings ***
Resource        cli_resource.robot
Test Template   Run Tests and Verify RC

*** Variables ***
${PASSING}      misc/normal.robot
${FAILING}      misc/pass_and_fail.robot

*** Test Cases ***
Zero RC when all tests pass
    ${EMPTY}                    ${PASSING}      rc=0
    --statusrc                  ${PASSING}      rc=0

Non-zero RC when tests fail
    ${EMPTY}                    ${FAILING}      rc=1
    -r report.html              ${FAILING}      rc=1
    -l log.html --statusrc      ${FAILING}      rc=1

Zero RC when all tests pass with --NoStatusRC
    --NoStatusRC                 ${PASSING}     rc=0

Zero RC when tests fail with --NoStatusRC
    --nostatusrc                 ${FAILING}     rc=0

--StatusRC and --NoStatusRC together
    --nostatusrc --statusrc     ${FAILING}      rc=1
    --Status --NoStatus --Status --Status --Status --NoStatus
    ...                         ${FAILING}      rc=0

*** Keywords ***
Run Tests and Verify RC
    [Arguments]    ${options}    ${source}    ${rc}
    ${result} =    Run Tests Without Processing Output    ${options}    ${source}
    Should Be Equal As Integers    ${result.rc}    ${rc}
    Should Be Empty    ${result.stderr}
