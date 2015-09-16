*** Settings ***
Resource        cli_resource.robot
Test Template   Run Tests and Verify RC

*** Variables ***
${MISCDIR}   ${CURDIR}/../../../testdata/misc
${PASSING}   ${MISCDIR}/normal.robot
${FAILING}   ${MISCDIR}/pass_and_fail.robot

*** Test Cases ***
Zero RC when all tests pass
    ${PASSING}                             rc=0
    --statusrc ${PASSING}                  rc=0

Zero RC when all critical tests pass
    --critical pass ${FAILING}             rc=0
    -c pass --status ${FAILING}            rc=0

Non-zero RC when critical tests fail
    ${FAILING}                             rc=1
    -r report.html ${FAILING}              rc=1
    -l log.html --statusrc ${FAILING}      rc=1

Zero RC when all tests pass with --NoStatusRC
    --NoStatusRC ${PASSING}                rc=0

Zero RC when critical tests fail with --NoStatusRC
    --nostatusrc ${FAILING}                rc=0

--StatusRC and --NoStatusRC together
    --nostatusrc --statusrc ${FAILING}                    rc=1
    --Status --NoStatus --Status --NoStatus ${FAILING}    rc=0

*** Keywords ***
Run Tests and Verify RC
    [Arguments]    ${options & source}    ${rc}
    ${returned}=    Run And Return Rc    ${ROBOT} -o NONE -l NONE -r NONE ${options & source}
    Should Be Equal As Integers    ${returned}    ${rc}
