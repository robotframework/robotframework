*** Settings ***
Suite Setup     Generate input files
Suite Teardown  Remove input files
Test Template   Run Rebot and Verify RC
Resource        rebot_cli_resource.robot

*** Variables ***
${PASSING}         %{TEMPDIR}${/}rebot-testing-passing.xml
${FAILING}         %{TEMPDIR}${/}rebot-testing-failing.xml
${REPORT}          %{TEMPDIR}${/}robot-testing-report.html
${NO OUTPUTS}      [ ERROR ] No outputs created.\n\nTry --help for usage information.

*** Test Cases ***
Zero RC when all tests pass
    ${PASSING}                       rc=0

Zero RC when all critical tests pass
    --critical pass ${FAILING}       rc=0
    --statusrc -c pass ${FAILING}    rc=0

Non-zero RC when critical tests fail
    ${FAILING}                       rc=1
    --status ${FAILING}              rc=1

Zero RC when all tests pass with --NoStatusRC
    --NoStatusRC ${PASSING}          rc=0

Zero RC when critical tests fail with --NoStatusRC
    --nostatusrc ${FAILING}          rc=0

Error when no output is created
    ${PASSING}                       rc=252    output=${NO OUTPUTS}  report=NONE
    --nostatusrc ${FAILING}          rc=252    output=${NO OUTPUTS}  report=NONE

--StatusRC and --NoStatusRC together
    --nostatusrc --statusrc ${FAILING}                        rc=1
    --Status --NoStatus --Status --NoStatus ${FAILING}        rc=0

*** Keywords ***
Generate input files
    Run Tests Without Processing Output  ${EMPTY}  misc/normal.robot
    Move File  ${OUTFILE}  ${PASSING}
    Run Tests Without Processing Output  ${EMPTY}  misc/pass_and_fail.robot
    Move File  ${OUTFILE}  ${FAILING}

Remove input files
    Remove Files  ${PASSING}  ${FAILING}

Run Rebot and Verify RC
    [Arguments]  ${options & source}  ${rc}=  ${output}=  ${report}=${REPORT}
    ${returned rc}  ${returned output} =  Run And Return RC And Output
    ...  ${INTERPRETER.rebot} --log NONE --report ${report} ${options & source}
    Should Be Equal As Integers  ${returned rc}  ${rc}
    Run Keyword If  """${output}"""  Should Be Equal  ${returned output}  ${output}
