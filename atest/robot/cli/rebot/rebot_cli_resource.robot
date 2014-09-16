*** Settings ***
Resource  ../runner/cli_resource.robot

*** Variables ***
${TEST FILE}      misc${/}normal.robot
${MYOUTDIR}       %{TEMPDIR}${/}rebot-cli-output
${MYINPUT}        %{TEMPDIR}${/}rebot-cli-input.xml
${M_211_211}      2 critical tests, 1 passed, 1 failed\n 2 tests total, 1 passed, 1 failed
${M_110_211}      1 critical test, 1 passed, 0 failed\n 2 tests total, 1 passed, 1 failed
${M_101_211}      1 critical test, 0 passed, 1 failed\n 2 tests total, 1 passed, 1 failed
${M_000_211}      0 critical tests, 0 passed, 0 failed\n 2 tests total, 1 passed, 1 failed


*** Keywords ***

Run tests to create input file for Rebot
    [Arguments]    ${tests}=${TESTFILE}    ${input}=${MYINPUT}
    Run Tests Without Processing Output  --loglevel TRACE  ${tests}
    Move File  ${OUTFILE}  ${input}
    Create Directory  ${MYOUTDIR}

Remove temporary files
    Remove Directory  ${MYOUTDIR}  recursively
    Remove File  ${MYINPUT}

Empty output directory
    Empty Directory  ${MYOUTDIR}

Run rebot and return outputs
    [Arguments]  ${arguments}
    Empty output directory
    Set Runners
    Run  ${REBOT} --outputdir ${MYOUTDIR} ${arguments} ${MYINPUT}
    @{outputs} =  List Directory  ${MYOUTDIR}
    [Return]  @{outputs}
