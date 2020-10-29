*** Settings ***
Suite Setup     Generate input files
Suite Teardown  Remove input files
Test Template   Run Rebot and Verify RC
Resource        rebot_cli_resource.robot

*** Variables ***
${PASSING}         %{TEMPDIR}${/}rebot-testing-passing.xml
${FAILING}         %{TEMPDIR}${/}rebot-testing-failing.xml
${NO OUTPUTS}      [ ERROR ] No outputs created.\n\nTry --help for usage information.

*** Test Cases ***
Zero RC when all tests pass
    ${EMPTY}                   ${PASSING}        rc=0

Non-zero RC when tests fail
    ${EMPTY}                   ${FAILING}        rc=1
    --status                   ${FAILING}        rc=1

Zero RC when all tests pass with --NoStatusRC
    --NoStatusRC               ${PASSING}        rc=0

Zero RC when tests fail with --NoStatusRC
    --nostatusrc               ${FAILING}        rc=0

Error when no output is created
    ${EMPTY}                   ${PASSING}        rc=252    stderr=${NO OUTPUTS}    report=NONE
    --nostatusrc               ${FAILING}        rc=252    stderr=${NO OUTPUTS}    report=NONE

--StatusRC and --NoStatusRC together
    --nostatusrc --statusrc    ${FAILING}        rc=1
    --Status --NoStatus --Status --NoStatus --Status --Status --NoStatus
    ...                        ${FAILING}        rc=0

*** Keywords ***
Generate input files
    Run Tests Without Processing Output    ${EMPTY}    misc/normal.robot
    Move File    ${OUTFILE}    ${PASSING}
    Run Tests Without Processing Output    ${EMPTY}    misc/pass_and_fail.robot
    Move File    ${OUTFILE}    ${FAILING}

Remove input files
    Remove Files  ${PASSING}  ${FAILING}

Run Rebot and Verify RC
    [Arguments]    ${options}    ${source}    ${rc}=    ${stderr}=    ${report}=report.html
    ${result} =    Run Rebot Without Processing Output    --output NONE --report ${report} ${options}    ${source}
    Should Be Equal As Integers  ${result.rc}  ${rc}
    Should Be Equal    ${result.stderr}    ${stderr}
